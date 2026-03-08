import inspect


async def run_count(db, date_range):
    try:
        result = []
        for i in date_range:
            data = await db.filter(
                create_time__gte=f"{i} 00:00:00", create_time__lte=f"{i} 23:59:59"
            ).count()
            result.append(data)
        return result
    except Exception as e:
        return []


async def get_count_all(db):
    try:
        result = await db.all().values()
        num = 0
        for i in result:
            num += len(i["script"])
        return num
    except Exception as e:
        return -1
