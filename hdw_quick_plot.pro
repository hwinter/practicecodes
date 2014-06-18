pro hdw_quick_plot, output
;
;Name: hdw_quick_plot
;
;Purpose: creates three dummy data files in two column format
;
;Inputs:None
;
;Outputs: three files plota.data, plotb.data, plotc.data and returns y
;
;
;Example: hdw_quick_plot, outy
;
;Edited: by Daniel Herman, 6/18/14, daniel.herman@cfa.harvard.edu
;
; 
n_points=100

X = 2*!PI/(n_points-1) * FINDGEN(n_points)
y=dblarr(3, n_points)

y[0,*]= SIN(X)
y[1,*]=SIN(3*X)
y[2,*]=3*SIN(X/2)+1 

file=strarr(3)

file[0]='plota.data'
file[1]='plotb.data'
file[2]='plotc.data'

for i=0ul, n_elements(file)-1 do begin
   openw,lun,FILE[i],/get_lun
   printf, lun, 'This is file '+file[i]
   printf, lun, 'File created on: ', systime(/UTC)+'.'
   for j=0ul, n_points-1 do begin
      printf,lun,'     ',x[j],'    ',y[i,j]
   endfor
   printf, lun, 'EOF'
   free_lun,lun
endfor
output = y
end
