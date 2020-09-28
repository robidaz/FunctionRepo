import inspect
def filter_dict(dict_to_filter, target_function):
    """Filters out dictionary items that are not present as arguments of the target function"""
    filtered_dict = {}
    try:
        sig = inspect.signature(target_function)
        filter_keys = [param.name for param in sig.parameters.values(
        ) if param.kind == param.POSITIONAL_OR_KEYWORD]
        filtered_dict = {
            filter_key: dict_to_filter[filter_key] for filter_key in filter_keys}
    except KeyError:
        pass
    return filtered_dict