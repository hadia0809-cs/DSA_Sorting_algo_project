import operator

from data_store import FIELD_OF, TYPE_OF

TEXT_OPS = {
    "contains":         lambda cell, v: v in cell,
    "does not contain": lambda cell, v: v not in cell,
    "starts with":      lambda cell, v: cell.startswith(v),
    "ends with":        lambda cell, v: cell.endswith(v),
    "equals":           lambda cell, v: cell == v,
}
NUM_OPS = {
    "=": operator.eq, "≠": operator.ne, ">": operator.gt,
    "≥": operator.ge, "<": operator.lt, "≤": operator.le,
}


def build_predicate(header, op, text):
    field = FIELD_OF[header]
    kind = TYPE_OF[header]
    if op in TEXT_OPS:
        f, v = TEXT_OPS[op], text.lower()
        return lambda r: f(str(r[field]).lower(), v)
    if op in NUM_OPS:
        f = NUM_OPS[op]
        if kind == "int":
            try:
                v = int(text)
            except ValueError:
                raise ValueError(f"'{text}' is not a whole number")
            return lambda r: f(r[field], v)
        v = text.lower()                         # dates / text: compare as text
        return lambda r: f(str(r[field]).lower(), v)
    raise ValueError(f"Unknown operator: {op}")


def apply_filters(rows, conditions):
    preds = []
    for logic, header, op, text in conditions:
        if text.strip():
            preds.append((logic, build_predicate(header, op, text.strip())))
    if not preds:
        return list(rows)
    out = []
    for r in rows:
        result = preds[0][1](r)
        for logic, p in preds[1:]:
            if logic == "AND":
                result = result and p(r)
            elif logic == "OR":
                result = result or p(r)
            else:
                result = result and not p(r)
        if result:
            out.append(r)
    return out
