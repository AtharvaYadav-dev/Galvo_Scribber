def generate():
    matrix = [
        [1,1,1,1,1,1,1,0,0,0],
        [1,0,0,0,0,0,1,0,0,0],
        [1,0,1,1,1,0,1,0,0,0],
        [1,0,1,1,1,0,1,0,0,0],
        [1,0,1,1,1,0,1,0,0,0],
        [1,0,0,0,0,0,1,0,0,0],
        [1,1,1,1,1,1,1,0,0,0],
    ]
    rows = len(matrix)
    cols = len(matrix[0])
    visited = [[False]*cols for _ in range(rows)]
    
    rects = []
    for y in range(rows):
        for x in range(cols):
            if matrix[y][x] and not visited[y][x]:
                w = 1
                while x + w < cols and matrix[y][x+w] and not visited[y][x+w]:
                    w += 1
                
                h = 1
                can_expand = True
                while y + h < rows and can_expand:
                    for k in range(w):
                        if not matrix[y+h][x+k] or visited[y+h][x+k]:
                            can_expand = False
                            break
                    if can_expand:
                        h += 1
                        
                for r in range(h):
                    for c in range(w):
                        visited[y+r][x+c] = True
                rects.append((x, y, w, h))
    print(rects)
generate()
