import csv
import io
import json
import math
import re
from collections import defaultdict
from datetime import datetime


POSITIVE_WORDS = {
    "love", "great", "good", "amazing", "happy", "glad", "excited", "thanks", "thank",
    "appreciate", "proud", "care", "caring", "sweet", "kind", "fun", "wonderful", "yes",
}
NEGATIVE_WORDS = {
    "angry", "mad", "upset", "sad", "hurt", "annoyed", "frustrated", "bad", "hate",
    "tired", "drained", "stressed", "anxious", "worried", "no", "never", "can't", "cant",
}
EMPATHY_WORDS = {
    "sorry", "understand", "hear you", "i hear", "you okay", "you ok", "here for you",
    "that makes sense", "proud of you", "i'm here", "im here",
}


def clamp_0_100(value):
    return max(0, min(100, int(round(value))))

def _expand_midrange(value, strength=0.45):
    """
    Expands values away from 50 to reduce mid-range clustering.
    strength in [0,1]; higher -> stronger expansion.
    """
    x = max(0.0, min(1.0, value / 100.0))
    # Logistic curve centered at 0.5
    k = 4.0 + 6.0 * strength
    logistic = 1.0 / (1.0 + math.exp(-k * (x - 0.5)))
    blended = (1.0 - strength) * x + strength * logistic
    return clamp_0_100(blended * 100.0)

def _strength_from_total(total):
    # Increase spread as dataset grows.
    return max(0.35, min(0.75, 0.35 + math.log10(total + 1) / 3.0))

def _scale_linear(value, min_v, max_v):
    if max_v <= min_v:
        return 50.0
    return max(0.0, min(100.0, (value - min_v) / (max_v - min_v) * 100.0))

def _scale_log(value, max_v):
    value = max(0.0, value)
    max_v = max(1.0, max_v)
    return max(0.0, min(100.0, (math.log1p(value) / math.log1p(max_v)) * 100.0))

def _scale_centered(value, mid, spread):
    if spread <= 0:
        return 50.0
    return max(0.0, min(100.0, 50.0 + ((value - mid) / spread) * 50.0))

def _parse_timestamp(raw):
    if raw is None:
        return None
    if isinstance(raw, (int, float)):
        try:
            return datetime.fromtimestamp(float(raw))
        except Exception:
            return None
    text = str(raw).strip()
    if not text:
        return None
    for fmt in (
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%m/%d/%Y %H:%M:%S",
        "%m/%d/%Y %H:%M",
        "%m/%d/%Y",
    ):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            pass
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except Exception:
        return None


def _tokenize(text):
    return re.findall(r"[a-zA-Z']+", (text or "").lower())


def _sentiment_score(text):
    tokens = _tokenize(text)
    if not tokens:
        return 0.0
    pos = sum(1 for t in tokens if t in POSITIVE_WORDS)
    neg = sum(1 for t in tokens if t in NEGATIVE_WORDS)
    return (pos - neg) / max(1, len(tokens))


def _empathy_score(text):
    lower = (text or "").lower()
    hits = sum(1 for phrase in EMPATHY_WORDS if phrase in lower)
    return hits


def parse_messages_from_upload(file_storage):
    filename = (file_storage.filename or "").lower()
    raw = file_storage.read()
    text = raw.decode("utf-8", errors="ignore")

    messages = []

    if filename.endswith(".json"):
        data = json.loads(text)
        records = data.get("messages", data) if isinstance(data, dict) else data
        if isinstance(records, list):
            for row in records:
                if not isinstance(row, dict):
                    continue
                messages.append(
                    {
                        "sender": row.get("sender") or row.get("from") or row.get("author") or "Unknown",
                        "text": row.get("text") or row.get("message") or row.get("body") or "",
                        "timestamp": _parse_timestamp(
                            row.get("timestamp") or row.get("time") or row.get("date")
                        ),
                    }
                )
    elif filename.endswith(".csv"):
        reader = csv.DictReader(io.StringIO(text))
        for row in reader:
            messages.append(
                {
                    "sender": row.get("sender") or row.get("from") or row.get("author") or "Unknown",
                    "text": row.get("text") or row.get("message") or row.get("body") or "",
                    "timestamp": _parse_timestamp(
                        row.get("timestamp") or row.get("time") or row.get("date")
                    ),
                }
            )
    else:
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split(":", 1)
            if len(parts) == 2 and len(parts[0]) < 40:
                sender = parts[0].strip() or "Unknown"
                body = parts[1].strip()
            else:
                sender = "Unknown"
                body = line
            messages.append({"sender": sender, "text": body, "timestamp": None})

    messages = [m for m in messages if (m.get("text") or "").strip()]
    messages.sort(key=lambda m: m["timestamp"] or datetime.min)
    return messages


def _std(values):
    if not values:
        return 0.0
    mean = sum(values) / len(values)
    return math.sqrt(sum((v - mean) ** 2 for v in values) / len(values))


def infer_parameters(messages):
    if not messages:
        raise ValueError("No valid messages found in the uploaded file.")

    # Pick the two most frequent senders to avoid skew when many labels exist.
    sender_counts = defaultdict(int)
    for m in messages:
        sender_counts[m["sender"]] += 1
    if not sender_counts:
        raise ValueError("No sender information found in messages.")

    sorted_senders = sorted(sender_counts.items(), key=lambda x: x[1], reverse=True)
    sender_a = sorted_senders[0][0]
    sender_b = sorted_senders[1][0] if len(sorted_senders) > 1 else "Person B"

    by_sender = {sender_a: [], sender_b: []}
    for m in messages:
        if m["sender"] == sender_a:
            by_sender[sender_a].append(m)
        else:
            # Map all other senders to Person B to keep volume balanced.
            by_sender[sender_b].append(m)

    count_a = len(by_sender[sender_a])
    count_b = len(by_sender[sender_b])
    total = max(1, count_a + count_b)

    timestamps = [m["timestamp"] for m in messages if m["timestamp"] is not None]
    if timestamps:
        span_days = max(1.0, (max(timestamps) - min(timestamps)).total_seconds() / 86400.0)
    else:
        span_days = max(1.0, total / 40.0)

    msgs_per_day = total / span_days
    mutual_frequency = clamp_0_100(_scale_log(msgs_per_day, 200.0))

    sentiments = {sender_a: [], sender_b: []}
    empathy_hits = 0
    positive_hits = 0
    negative_hits = 0
    lengths = {sender_a: [], sender_b: []}

    for sender, sender_msgs in by_sender.items():
        for m in sender_msgs:
            s = _sentiment_score(m["text"])
            sentiments[sender].append(s)
            empathy_hits += _empathy_score(m["text"])
            tokens = _tokenize(m["text"])
            positive_hits += sum(1 for t in tokens if t in POSITIVE_WORDS)
            negative_hits += sum(1 for t in tokens if t in NEGATIVE_WORDS)
            lengths[sender].append(len(_tokenize(m["text"])))

    avg_sent_a = sum(sentiments[sender_a]) / max(1, len(sentiments[sender_a]))
    avg_sent_b = sum(sentiments[sender_b]) / max(1, len(sentiments[sender_b]))
    sent_std_all = _std(sentiments[sender_a] + sentiments[sender_b])
    sentiment_mean = (avg_sent_a + avg_sent_b) / 2.0
    sentiment_mag = (abs(avg_sent_a) + abs(avg_sent_b)) / 2.0
    sentiment_diff = abs(avg_sent_a - avg_sent_b)
    # If both sentiments are near-neutral, alignment should be neutral-ish.
    alignment_raw = max(0.0, 1.0 - min(1.0, sentiment_diff / 0.25))
    alignment_weight = min(1.0, sentiment_mag / 0.12)
    sentiment_alignment = 50.0 + alignment_raw * alignment_weight * 50.0

    reciprocity_gap = abs(count_a - count_b) / total
    reciprocity = (1.0 - reciprocity_gap) ** 0.6 * 100.0

    empathy_density = empathy_hits / max(1, total)
    pos_ratio = positive_hits / max(1, positive_hits + negative_hits)
    empathy_component = _scale_linear(empathy_density, 0.0, 0.08)
    sentiment_component = _scale_centered(sentiment_mean, 0.0, 0.12)
    positivity_component = _scale_centered(pos_ratio, 0.5, 0.25)
    stability_component = _scale_linear(1.0 - min(1.0, sent_std_all), 0.4, 1.0)
    mutual_empathy = clamp_0_100(
        0.35 * empathy_component
        + 0.25 * sentiment_component
        + 0.2 * positivity_component
        + 0.2 * stability_component
    )
    mutual_compatability = clamp_0_100(
        0.35 * sentiment_alignment
        + 0.3 * reciprocity
        + 0.2 * stability_component
        + 0.15 * _scale_linear(sentiment_mag, 0.02, 0.18)
    )

    avg_len = (sum(lengths[sender_a]) + sum(lengths[sender_b])) / max(1, len(lengths[sender_a]) + len(lengths[sender_b]))
    length_component = _scale_linear(avg_len, 3.0, 25.0)
    freq_component = _scale_log(msgs_per_day, 200.0)
    mutual_strength = clamp_0_100(
        0.4 * reciprocity + 0.35 * length_component + 0.25 * freq_component
    )

    response_lags = {sender_a: [], sender_b: []}
    switches = 0
    for i in range(1, len(messages)):
        prev = messages[i - 1]
        curr = messages[i]
        if prev["sender"] == curr["sender"]:
            continue
        switches += 1
        if prev["timestamp"] and curr["timestamp"]:
            lag_min = (curr["timestamp"] - prev["timestamp"]).total_seconds() / 60.0
            lag_min = max(0.0, min(lag_min, 24 * 60))
            response_lags[curr["sender"]].append(lag_min)

    turn_taking = (switches / max(1, len(messages) - 1)) * 100.0
    if response_lags[sender_a] or response_lags[sender_b]:
        lag_diff = abs(
            (sum(response_lags[sender_a]) / max(1, len(response_lags[sender_a])))
            - (sum(response_lags[sender_b]) / max(1, len(response_lags[sender_b])))
        )
        lag_sync = 100.0 - min(100.0, lag_diff / 3.0)
    else:
        # No timestamps → infer from turn-taking to avoid a flat midpoint.
        lag_sync = _scale_centered(turn_taking, 50.0, 30.0)
    mutual_sync = clamp_0_100(0.6 * turn_taking + 0.4 * lag_sync)

    burstiness = 50.0
    if timestamps and len(timestamps) > 2:
        gaps = []
        for i in range(1, len(timestamps)):
            gaps.append((timestamps[i] - timestamps[i - 1]).total_seconds() / 60.0)
        burstiness = min(100.0, _std(gaps) / max(1.0, (sum(gaps) / len(gaps))) * 100.0)

    mutual_codependence = clamp_0_100(
        0.45 * burstiness + 0.35 * (100.0 - lag_sync) + 0.2 * _scale_log(msgs_per_day, 200.0)
    )

    def person_metrics(sender):
        sender_msgs = by_sender[sender]
        sender_sents = sentiments[sender]
        sender_lags = response_lags[sender]

        sent_std = _std(sender_sents)
        lag_mean = sum(sender_lags) / max(1, len(sender_lags))
        lag_std = _std(sender_lags)
        init_share = len(sender_msgs) / total

        temperament = clamp_0_100(
            _scale_centered(sum(sender_sents) / max(1, len(sender_sents)), 0.0, 0.12) * 0.7
            + _scale_linear(1.0 - min(1.0, sent_std), 0.3, 1.0) * 0.3
        )
        hot_cold = clamp_0_100(_scale_linear(sent_std, 0.02, 0.18) * 0.7 + _scale_linear(lag_std, 2.0, 120.0) * 0.3)
        distant = clamp_0_100(
            _scale_linear(lag_mean, 5.0, 180.0) * 0.7 + _scale_linear(1.0 - init_share, 0.0, 0.6) * 0.3
        )

        burned_out = 0.0
        if len(sender_msgs) >= 6:
            thirds = max(1, len(sender_msgs) // 3)
            first = sender_msgs[:thirds]
            last = sender_msgs[-thirds:]
            first_avg = sum(len(_tokenize(m["text"])) for m in first) / max(1, len(first))
            last_avg = sum(len(_tokenize(m["text"])) for m in last) / max(1, len(last))
            decay = max(0.0, first_avg - last_avg)
            burned_out = clamp_0_100(decay * 12.0 + max(0.0, -sum(sender_sents) / max(1, len(sender_sents)) * 80.0))
        else:
            burned_out = clamp_0_100(max(0.0, -sum(sender_sents) / max(1, len(sender_sents)) * 100.0))

        return temperament, hot_cold, distant, burned_out

    a_temp, a_hotcold, a_distant, a_burned = person_metrics(sender_a)
    b_temp, b_hotcold, b_distant, b_burned = person_metrics(sender_b)

    strength = _strength_from_total(total)
    inferred = {
        "mutualEmpathy": _expand_midrange(mutual_empathy, strength=strength),
        "mutualCompatability": _expand_midrange(mutual_compatability, strength=strength),
        "mutualFrequency": _expand_midrange(mutual_frequency, strength=strength),
        "mutualStrength": _expand_midrange(mutual_strength, strength=strength),
        "mutualSync": _expand_midrange(mutual_sync, strength=strength),
        "mutualCodependence": _expand_midrange(mutual_codependence, strength=strength),
        "personATemperarment": _expand_midrange(a_temp, strength=strength),
        "personAHotCold": _expand_midrange(a_hotcold, strength=strength),
        "personADistant": _expand_midrange(a_distant, strength=strength),
        "personABurnedOut": _expand_midrange(a_burned, strength=strength),
        "personBTemperarment": _expand_midrange(b_temp, strength=strength),
        "personBHotCold": _expand_midrange(b_hotcold, strength=strength),
        "personBDistant": _expand_midrange(b_distant, strength=strength),
        "personBBurnedOut": _expand_midrange(b_burned, strength=strength),
        "personAName": sender_a,
        "personBName": sender_b,
    }
    debug = {
        "total_messages": total,
        "sender_counts": dict(sorted_senders[:4]),
        "span_days": round(span_days, 2),
        "messages_per_day": round(msgs_per_day, 2),
        "avg_sent_a": round(avg_sent_a, 4),
        "avg_sent_b": round(avg_sent_b, 4),
        "sentiment_mean": round(sentiment_mean, 4),
        "sentiment_mag": round(sentiment_mag, 4),
        "sent_std_all": round(sent_std_all, 4),
        "sentiment_alignment": round(sentiment_alignment, 2),
        "pos_ratio": round(pos_ratio, 3),
        "reciprocity": round(reciprocity, 2),
        "avg_msg_len": round(avg_len, 2),
        "turn_taking": round(turn_taking, 2),
        "lag_sync": round(lag_sync, 2),
        "burstiness": round(burstiness, 2),
    }
    return inferred, debug
