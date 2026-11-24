import json,os,urllib.request,urllib.error,random,sys,hashlib
ENV=os.getenv('MAKEFUN_ENV_URL','')
if not ENV:sys.exit('no MAKEFUN_ENV_URL')
VALUE={'p':1,'n':3,'b':3,'r':5,'q':9,'k':100}
SEED=int(os.getenv('MAKEFUN_TRIAL_SEED','0'))
RCT=random.Random(SEED)

def post(path,raw):
    r=urllib.request.Request(ENV+path,data=json.dumps(raw).encode(),headers={'content-type':'application/json'})
    try:
        with urllib.request.urlopen(r) as res:
            return json.load(res)
    except urllib.error.HTTPError as e:
        sys.exit(f'{e.code} {e.read().decode(errors="replace")}')

def board_of(fen):
    b={}
    for i,r in enumerate(fen.split()[0].split('/')):
        c=0
        for ch in r:
            if ch.isdigit():
                c+=int(ch)
            else:
                b[chr(ord('a')+(c%8)) + str(8-i)] = ch
                c+=1
    return b

def legal_moves(board):
    n=len(board)
    moves=[[] for _ in range(8)]
    for s,p in board.items():
        if p=='k':continue
        file=int(s[0])-1;r=8-int(s[1])
        for dr,dc in [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]:
            af,ar=r+dr,r+dc
            if 0<=af<8 and 0<=ar<8:
                ns=chr(ord('a')+file+dc)+str(8-af)
                to=board.get(ns)
                promo=None
                if p.lower()=='p' and 0<=af<2:
                    promo='bnrq'.rfind(p)+1
                if not to or p[0].isupper()!=to[0].isupper():
                    moves[file+r*8].append((ns,to,promo))
    return moves

def position_value(board):
    return sum(VALUE.get(p.lower(),0) for p in board.values())

def board_clone(board,move,to,promo):
    board2=board.copy()
    board2[move]=to.lower()
    # Capture: overwrite captured piece
    try:
        board2[move[0]+move[1]]=board[move[0]+move[1]]
    except:
        pass
    if promo:
        board2[move]=promo.lower()
    return board2

def minimax(board,seed,depth,alpha,beta):
    if depth<=0:
        return position_value(board)
    md=legal_moves(board)
    maxv=-1e9
    for m,to,promo in md[len(board)//8]:
        if to is None:
            continue
        board2=board_clone(board,m,to,promo)
        v=-minimax(board2,seed+1,depth-1,-beta,-alpha)
        if v>maxv:
            maxv=v
        if v>alpha:
            alpha=v
        if alpha>=beta:
            break
    return maxv

def choose(fen,legal):
    board=board_of(fen)
    depth=int(SEED)%5+1
    best=None
    maxv=-1e9
    for m in legal:
        board2=board_clone(board,m,m[2:4],m[4] if len(m)==5 else None)
        v=minimax(board2,0,depth-1,-1e9,1e9)
        if v>maxv:
            maxv=v
            best=m
    return best if best is not None else legal[0]

while True:
    g=post('/game',{})
    if g['status']=='done':break
    while g['status']=='your_move':
        g=post('/move',{'game':g['game'],
                        'move':choose(g['fen'],g['legal_moves'])})
    print(f'game {g["game"]}: {g["outcome"]} by {g["reason"]}',file=sys.stderr)
print(f'done: {g.get("wins")} won, {g.get("draws")} drawn, {g.get("losses")} lost',file=sys.stderr)
