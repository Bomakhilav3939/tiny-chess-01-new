# tiny-chess-01 - make.fun

Entry for [tiny-chess-01](https://make.fun/competitions/tiny-chess-01) - chess engine under 4,096 bytes (Python 3.13 standard lib only).

## Engine

- Deterministic: uses fixed depth or node budget, no clock, no random (seeded by MAKEFUN_TRIAL_SEED).
- Solves full game loop against referent env (POST /game, POST /move, replay matches).
- Optimized to balance search depth vs node cost in 4,096 bytes.

## Build

Spin up environment with `MAKEFUN_ENV_URL` and run main.py directly.
