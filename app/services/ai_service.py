"""AI 分级服务：语音转写后的急救预判。

骨架阶段用关键词规则给出可运行的分级结果与摘要，接口形态与真实大模型一致；
接入 LLM / ASR 时只需替换本文件内部实现，路由层无需改动。
"""

from ..models import OrderLevel

# 高危关键词：命中即判为 L3，需同步通知 120
CRITICAL_KEYWORDS = ('晕倒', '昏迷', '没有呼吸', '呼吸困难', '胸痛', '吐血', '出血不止', '抽搐', '倒地')
# 中危关键词：判定为 L2，派就近救护员上门
URGENT_KEYWORDS = ('摔', '疼', '头晕', '胸闷', '心慌', '站不起来', '起不来', '难受')

LEVEL_DESC = {
    OrderLevel.L1: '非紧急，需要人陪护确认',
    OrderLevel.L2: '紧急但暂不需要 120，就近救护员上门',
    OrderLevel.L3: '危重，立即呼叫 120 并同步家属',
}


def grade_emergency(transcript: str = '', signals: dict | None = None) -> dict:
    """根据语音转写与传感器信号给出分级、摘要与是否呼叫 120。

    参数
    ----
    transcript: ASR 转写文本，可为空（纯敲击触发时无语音）
    signals: 传感器信号，如 {"knock_count": 3, "fall_detected": True}
    """

    text = (transcript or '').strip()
    signals = signals or {}

    level = OrderLevel.L2
    need_120 = False
    reason = '仅触发求助信号，未获取到语音信息，按默认等级派单'

    if any(word in text for word in CRITICAL_KEYWORDS):
        level, need_120 = OrderLevel.L3, True
        reason = '语音中出现危重关键词，判定为需立即呼叫 120'
    elif any(word in text for word in URGENT_KEYWORDS):
        level = OrderLevel.L2
        reason = '语音中出现不适或跌倒相关描述，判定为需就近救护员上门'
    elif text:
        level, need_120 = OrderLevel.L1, False
        reason = '语音未见紧急描述，建议由家属或救护员确认情况'

    if signals.get('fall_detected') and level != OrderLevel.L3:
        level = OrderLevel.L2
        reason = '检测到疑似跌倒信号'

    summary_parts = [f'【分级 {level}】{LEVEL_DESC[level]}']
    if signals.get('knock_count'):
        summary_parts.append(f'触发方式：连续敲击 {signals["knock_count"]} 次')
    if text:
        summary_parts.append(f'语音转写：{text[:60]}')
    if signals.get('fall_detected'):
        summary_parts.append('传感器：检测到疑似跌倒')

    return {
        'level': level,
        'need_120': need_120,
        'summary': '；'.join(summary_parts),
        'reason': reason,
        # TODO: 接入大模型后返回真实置信度与结构化字段（意识/呼吸/出血等）
        'confidence': 0.6,
    }
