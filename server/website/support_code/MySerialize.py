from datetime import datetime


def serialize(obj_model: object, exclude: tuple[str] = None):
    main_dict: dict = obj_model.__dict__.copy()
    try:
        main_dict.pop('_state')
    except:
        pass

    for key in main_dict:
        value = main_dict[key]
        if isinstance(value, datetime):
            main_dict[key] = str(value)

    if exclude is not None:
        for field in exclude:
            del main_dict[field]
    return main_dict
