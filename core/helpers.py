import isodate
from config import MAX_TITLE_LEN


def to_bold_unicode(text):
    maps = {
        'A': '𝗔', 'B': '𝗕', 'C': '𝗖', 'D': '𝗗', 'E': '𝗘', 'F': '𝗙', 'G': '𝗚', 'H': '𝗛',
        'I': '𝗜', 'J': '𝗝', 'K': '𝗞', 'L': '𝗟', 'M': '𝗠', 'N': '𝗡', 'O': '𝗢', 'P': '𝗣',
        'Q': '𝗤', 'R': '𝗥', 'S': '𝗦', 'T': '𝗧', 'U': '𝗨', 'V': '𝗩', 'W': '𝗪', 'X': '𝗫',
        'Y': '𝗬', 'Z': '𝗭', 'a': '𝗮', 'b': '𝗯', 'c': '𝗰', 'd': '𝗱', 'e': '𝗲', 'f': '𝗳',
        'g': '𝗴', 'h': '𝗵', 'i': '𝗶', 'j': '𝗷', 'k': '𝗸', 'l': '𝗹', 'm': '𝗺', 'n': '𝗻',
        'o': '𝗼', 'p': '𝗽', 'q': '𝗾', 'r': '𝗿', 's': '𝘀', 't': '𝘁', 'u': '𝘂', 'v': '𝘃',
        'w': '𝘄', 'x': '𝗲', 'y': '𝘆', 'z': '𝘇', '0': '𝟬', '1': '𝟭', '2': '𝟮', '3': '𝟯',
        '4': '𝟰', '5': '𝟱', '6': '𝟲', '7': '𝟟', '8': '𝟴', '9': '𝟵',
    }
    return "".join(maps.get(c, c) for c in text)


def one_line_title(full_title):
    if len(full_title) <= MAX_TITLE_LEN:
        return full_title
    return full_title[: MAX_TITLE_LEN - 1] + "…"


def parse_duration_str(duration_str):
    try:
        return int(isodate.parse_duration(duration_str).total_seconds())
    except Exception:
        if ":" in str(duration_str):
            try:
                parts = [int(x) for x in str(duration_str).split(":")]
                if len(parts) == 2:
                    return parts[0] * 60 + parts[1]
                if len(parts) == 3:
                    return parts[0] * 3600 + parts[1] * 60 + parts[2]
            except Exception:
                pass
        return 0


def format_time(seconds):
    secs = int(seconds)
    m, s = divmod(secs, 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def get_progress_bar(elapsed, total, bar_length=14):
    if total <= 0:
        return "LIVE 🔴"
    fraction = min(elapsed / total, 1)
    marker_index = min(int(fraction * bar_length), bar_length - 1)
    left = "━" * marker_index
    right = "─" * (bar_length - marker_index - 1)
    return f"{format_time(elapsed)} {left}❄️{right} {format_time(total)}"


def get_readable_time(seconds):
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]
    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)
    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "
    time_list.reverse()
    ping_time += ":".join(time_list)
    return ping_time
