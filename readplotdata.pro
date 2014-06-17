function readplotdata, data1,data2,data3, psname, totalplot
;
;Name: readplotdata
;
;Purpose:read two columns of data and creates a postscript of the plotted data
;
;Inputs: data1/2/3 are ascii files with 2 columns, psname is the name for the postscipt
; names
;
;Outputs: totalplot is an an array of 6 arrays representing the first and second columns 
; data 1/2/3 respectively
;
;Example: readplotdata('foo.txt','bar.txt','crum.txt', 'data1',totalplot)
;
;Written:6/17/13 Daniel Herman, daniel.herman@cfa.harvard.edu
;
;
; Define color table
ct =  {black    : 0, $
          white     : 1, $
          red       : 2, $
          green     : 3, $
          blue      : 4, $
          yellow    : 5, $
          magenta   : 6, $
          cyan      : 7, $
          orange    : 8} 
; Next I create red/green/blue vectors with value combinations that 
; give us the colors we want
;          0     1       2       3       4        5       6      7      8 
rr =  [  0, 255,   255,  0,      0,      255,  255, 0,     255]
gg = [  0, 255,   0,      255,  0,      255,  0,     255, 125]
bb = [  0, 255,   0,      0,      255,  0,      255, 255,  0]
; Lastly, we load the new color table
tvlct, rr, gg, bb
;read the ascii files into vectors
readcol, data1, aV1, aV2, comment = 'E', format = 'F,F', skipline = 2
plotdata1 = [[aV1],[aV2]]
readcol, data2, bV1, bV2, comment = 'E', format = 'F,F', skipline = 2
plotdata2 = [[bV1],[bV2]]
readcol, data3, cV1, cV2, comment = 'E', format = 'F,F', skipline = 2
plotdata3 = [[cV1],[cV2]]
;create return variable
totalplot = [[plotdata1],[plotdata2],[plotdata3]]
;Initialize postscript device
set_plot, 'PS'
device, /encapsulated, xsize = 8, ysize = 4, /inches,/portrait,/color, decomposed = 0,$
bits_per_pixel=8, filename = '~/Documents/'+psname+'.eps'
font=3 & charsize = 2
axis_thick=6 & line_thick=6
;Plotting commands
plot, cV1, cV2, color=ct.black, /nodata, xthick=axis_thick, ythick=axis_thick,font =font,$
thick=line_thick,charsize=charsize,xtitle = 'time', ytitle = 'flux', title = 'Dummy Plot',$
xrange=[0,6],yrange=[-1,5]
oplot, aV1, aV2, color = ct.red, thick = line_thick
oplot, bV1, bV2, color = ct.blue, line = 3, thick = line_thick 
oplot, cV1, cV2, color = ct.green, line=2,thick=line_thick
device, /close ;completes PS file
set_plot, 'x'
return, totalplot
end