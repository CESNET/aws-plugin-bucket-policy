# -*- coding: utf-8 -*-
#

try:
    from iterfzf import iterfzf
    USE_FZF=True
except ModuleNotFoundError:
    USE_FZF=False

#USE_FZF=False

def sel(options, nofzf=False):
    if USE_FZF and not nofzf:
        return(iterfzf(options))
    else:
        arr = enumerate(options)
        n = len(options)
        for k,v in arr: print(f'{k+1}: ',v)
        msg = f'Select number (1-{n}): '
        selk = None
        while True:
            try:
                selk = int(input(msg))
                if selk in range(1, n+1): break
            except KeyboardInterrupt as e:
                raise e
            except:
                pass
            msg = f'Invalid option, select again (1-{n}): '
        return(options[selk-1])

__all__ = ('USE_FZF', 'sel')
