import numpy as np
import pygame as pg
from pygame import Rect

import initializer


#########################################################
# Grid and window
CELLSIZE = 10
H_CELLSIZE = CELLSIZE//2
CELLGAP = 1
GRID_X,GRID_Y = 80,80
WINDOW_DIMS = (GRID_X*(CELLSIZE+CELLGAP)+CELLSIZE,
                 GRID_Y*(CELLSIZE+CELLGAP)+CELLSIZE)

# State update times (speeds)
PERIODS = [50, 70, 90, 150, 250, 450, 900]
period_index = 3

# Storing previous states for rewind
STATES_STORED = 50
previous_states = [ (np.array([]),np.array([])) ]*STATES_STORED
prev_st = STATES_STORED

pg.init()
screen = pg.display.set_mode(WINDOW_DIMS)
clock = pg.time.Clock()
# State update period (ms)
pg.time.set_timer(pg.USEREVENT, PERIODS[period_index])

grid = None
paused=False
mousedown=False
#########################################################



def sum_vonneuman_nn(arr,i,j):
    """Count nearest neighbours (from von Neuman neighourhood)"""
    rows,cols=arr.shape
    nn = arr[(i-1)%rows][(j-1)%cols] + arr[(i-1)%rows][(j+1)%cols] + \
            arr[(i+1)%rows][(j-1)%cols] + arr[(i+1)%rows][(j+1)%cols] + \
            arr[(i-1)%rows][j] + arr[i][(j+1)%cols] + \
            arr[(i+1)%rows][j] + arr[i][(j-1)%cols]
    return nn


def update_gol(arr):
    """Update array based on classical rules"""
    nxt = np.zeros(arr.shape)
    rows,cols = nxt.shape
    for i in range(rows):
        for j in range(cols):
            nn = sum_vonneuman_nn(arr,i,j)
            if arr[i][j]==1:
                if nn==2 or nn==3:
                    nxt[i][j]=1
            else:
                if nn==3:
                    nxt[i][j]=1
    return nxt


def mouse_to_grid( pos ):
    """Convert mouse click coords to grid indices

    Return None if clicking in H_CELLSIZE window border region
    """
    mx,my=pos
    # account for window border and gap between cells
    ix = int((mx-H_CELLSIZE)/(CELLSIZE+CELLGAP))
    iy = int((my-H_CELLSIZE)/(CELLSIZE+CELLGAP))
    # force respect window borders
    if ix<0 or ix>=GRID_X or iy<0 or iy>=GRID_Y:
        return None
    else:
        return (ix,iy)


def grid_to_mouse( pos ):
    """Convert grid indices to pixel coordinates
    """
    ix,iy=pos
    px= ix*CELLSIZE + H_CELLSIZE + ix*CELLGAP
    py= iy*CELLSIZE + H_CELLSIZE + iy*CELLGAP
    return (px,py)


def keyup(event):
    """Key release events"""
    global paused
    global grid
    global period_index
    global prev_st
    global previous_states

    # Enter key for (un)pausing
    if event.key==pg.K_RETURN:
        if paused:
            paused=False
            # reset stored states after each un-pause
            previous_states=[(np.array([]),np.array([]))]*STATES_STORED
            prev_st = STATES_STORED-1
        else:
            paused=True
    # C key for clearing grid
    if event.key == pg.K_c:
        grid = np.zeros((GRID_X,GRID_Y))
    # Up/down for changing speed
    if event.key==pg.K_UP:
        if period_index-1>=0:
            period_index -= 1
            pg.time.set_timer(pg.USEREVENT, PERIODS[period_index])
    if event.key==pg.K_DOWN:
        if period_index+1<len(PERIODS):
            period_index += 1
            pg.time.set_timer(pg.USEREVENT, PERIODS[period_index])
    # Left/right for rewind/advacing stored states
    if event.key==pg.K_LEFT and paused:
        if prev_st-1>=0:
            prev_st-=1
            new_st = previous_states[prev_st]
            if new_st != ():
                grid = np.zeros((GRID_X,GRID_Y))
                for x,y in zip(new_st[0],new_st[1]):
                    grid[x][y]=1
    if event.key==pg.K_RIGHT and paused:
        if prev_st+1 < STATES_STORED:
            # Find next stored state
            prev_st+=1
            new_st = previous_states[prev_st]
            if new_st != ():
                grid = np.zeros((GRID_X,GRID_Y))
                for x,y in zip(new_st[0],new_st[1]):
                    grid[x][y]=1
        else:
            # Update as normal
            grid = update_gol(grid)
            # Store state for rewind/advance feature
            live_cells = np.nonzero(grid)
            fixed = is_fixed_state( previous_states[-1], live_cells )
            if not fixed:
                previous_states.pop(0)
                previous_states.append( live_cells )
    
        


def is_fixed_state( previous_live, live_cells ):
    """Check current live cells against previous state

    tuple of (arr_x, arr_y)
    """
    fixed = False
    if previous_live[0].size == live_cells[0].size:
        if previous_live[1].size == live_cells[1].size:
            if (previous_live[0]==live_cells[0]).all():
                if (previous_live[1]==live_cells[1]).all():
                    fixed = True
    return fixed
       




def main():
    global grid, paused, mousedown, previous_states

    # Set a starting configuration
    grid = np.zeros((GRID_X,GRID_Y))
    #grid = initializer.random_state( grid, density=0.2)
    #grid = initializer.glider( grid )
    grid = initializer.copperhead( grid )
    #grid = initializer.lightweight_spaceship( grid )


    while True:

        # Buttons/mouse
        if pg.event.get(pg.QUIT): 
            break
        for e in pg.event.get():
            # Click and drag for drawing
            if e.type==pg.MOUSEBUTTONDOWN and not mousedown:
                mousedown=True
            elif e.type==pg.MOUSEBUTTONUP and mousedown:
                mousedown=False
            # Keys for pausing and clearing screen
            if e.type == pg.KEYUP:
                keyup(e)
            # Updating grid in regular time steps
            if e.type == pg.USEREVENT:
                if not paused:
                    grid = update_gol(grid)
                    # Store state for rewind/advance feature
                    live_cells = np.nonzero(grid)
                    # dont store state if no change
                    fixed = is_fixed_state( previous_states[-1], live_cells )
                    if not fixed:
                        previous_states.pop(0)
                        previous_states.append( live_cells )
        
        if mousedown:
            # Get mouse state: boolean ints (left, middle, right)
            # Draw if left, delete if right click       
            mousestate = pg.mouse.get_pressed()
            mousepos=pg.mouse.get_pos()
            gridpos = mouse_to_grid(mousepos)
            if gridpos is not None:
                ix,iy=gridpos
                if mousestate[0]==1:
                    grid[ix][iy]=1
                elif mousestate[2]==1:
                    grid[ix][iy]=0


        # Get x,y indices of live cells to draw
        live_cells = np.nonzero(grid)
        xs,ys=list(live_cells)[0],list(live_cells[1]) 
        # Pause if all dead
        if len(xs)==0:
            paused=True

        
        # Draw current state to screen
        screen.fill(pg.color.Color('grey'))
        for ix,iy in zip(xs,ys):
            px,py = grid_to_mouse( (ix,iy) )
            if paused:
                pg.draw.rect(screen, pg.color.Color(150,150,150), Rect(px,py,CELLSIZE,CELLSIZE) )
            else:
                pg.draw.rect(screen, pg.color.Color(0,84,64), Rect(px,py,CELLSIZE,CELLSIZE) )
        pg.display.flip()



if __name__=="__main__":
    main()



