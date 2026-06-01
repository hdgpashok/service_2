def orm_to_dict(obj):
    if not obj:
        return {}
    return {
        column.name: getattr(obj, column.name)
        for column in obj.__table__.columns
    }