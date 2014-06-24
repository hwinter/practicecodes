import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os
import sunpy
import glob
import sunpy.map
import numpy as np

def _blit_draw(self, artists, bg_cache):
    # Handles blitted drawing, which renders only the artists given instead
    # of the entire figure.
    updated_ax = []
    for a in artists:
        # If we haven't cached the background for this axes object, do
        # so now. This might not always be reliable, but it's an attempt
        # to automate the process.
        if a.axes not in bg_cache:
            # bg_cache[a.axes] = a.figure.canvas.copy_from_bbox(a.axes.bbox)
            # change here
            bg_cache[a.axes] = a.figure.canvas.copy_from_bbox(a.axes.figure.bbox)
        a.axes.draw_artist(a)
        updated_ax.append(a.axes)

    # After rendering all the needed artists, blit each axes individually.
    for ax in set(updated_ax):
        # and here
        # ax.figure.canvas.blit(ax.bbox)
        ax.figure.canvas.blit(ax.figure.bbox)

# MONKEY PATCH!!
animation.ArtistAnimation._blit_draw = _blit_draw

def dih_sunmovie1(imagedir,savename):
	# Set up formatting for the movie files
    Writer = animation.writers['ffmpeg']
    writer = Writer(fps=15, metadata=dict(artist='Me'), bitrate=1800)
 
    # Get some data
    filenames = sorted(os.listdir(imagedir))
    print filenames 
    fig = plt.figure("An SDO movie")
    img = []
    for x in filenames:
    	print("Processing %s" % x)
    	im = sunpy.map.Map(os.path.join(imagedir, x))
    	img.append([im.plot()])
 
    ani = animation.ArtistAnimation(fig, img, interval=20, blit=True,repeat_delay=0)
    ani.save(savename, writer=writer)
    return img