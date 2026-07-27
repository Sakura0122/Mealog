from datetime import date, datetime, time, timedelta


def get_date_range(target_date: date) -> tuple[datetime, datetime]:
    """
    获取某个日期对应的左闭右开时间范围。

    :param target_date: 目标日期
    :return: 当天开始时间和次日开始时间
    """

    start_at = datetime.combine(target_date, time.min)
    return start_at, start_at + timedelta(days=1)


def get_month_range(month: str) -> tuple[datetime, datetime]:
    """
    获取某个月份对应的左闭右开时间范围。

    :param month: 目标月份，格式为 YYYY-MM
    :return: 当月开始时间和下月开始时间
    """

    start_at = datetime.strptime(month, "%Y-%m")
    if start_at.month == 12:
        return start_at, start_at.replace(year=start_at.year + 1, month=1)
    return start_at, start_at.replace(month=start_at.month + 1)
