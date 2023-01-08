def _check_collisio_nonsymmetric(entity1, entity2):
    x1, y1 = entity1.x, entity1.y
    x1start = x1 - entity1.width / 2
    x1end = x1 + entity1.width / 2
    y1start = y1 - entity1.height / 2
    y1end = y1 + entity1.height / 2

    x2, y2 = entity2.x, entity2.y
    x2start = x2 - entity2.width / 2
    x2end = x2 + entity2.width / 2
    y2start = y2 - entity2.height / 2
    y2end = y2 + entity2.height / 2
    
    horizontal = x1start <= x2start <= x1end or x1start <= x2end <= x1end
    vertical = y1start <= y2start <= y1end or y1start <= y2end <= y1end
    
    return vertical and horizontal

def check_collision(entity1, entity2):
    ns1 = _check_collisio_nonsymmetric(entity1, entity2)
    ns2 = _check_collisio_nonsymmetric(entity2, entity1)
    return ns1 or ns2
