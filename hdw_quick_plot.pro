n_points=100

X = 2*!PI/(n_points-1) * FINDGEN(n_points)
y=dblarr(3, n_points)

y[0,*]= SIN(X)
y[1,*]=SIN(3*X)
y[2,*]=3*SIN(X/2)+1 

file=strarr(3)

file[0]='plot1.data'
file[1]='plot2.data'
file[2]='plot3.data'

for iii=0ul, n_elements(file)-1 do begin
   openw,lun,FILE[iii],/get_lun
   printf, lun, 'This is file '+file[iii]
   printf, lun, 'File created on: ', systime(/UTC)+'.'
   for jjj=0ul, n_points-1 do begin
      printf,lun,'     ',x(jjj),'    ',y[iii,jjj]
   endfor
   printf, lun, 'EOF'
   free_lun,lun

endfor


end
