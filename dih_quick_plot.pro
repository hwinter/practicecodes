pro dih_quick_plot, nfiles, output
;
;Name: dih_quick_plot
;
;Purpose: creates many dummy data files in two column format
;
;Inputs: number of files to create
;
;Outputs: 
;
;
;Example: 
;
;Edited: by Daniel Herman, 6/18/14, daniel.herman@cfa.harvard.edu
;
; 
n_points=100 ;sets number of data points

X = 2*!PI/(n_points-1) * FINDGEN(n_points) ;creates x coordinates
y=dblarr(nfiles, n_points) ;creates y coordinate framework double array
ynoise = randomu(seed,n_points) ;creates noise framework array
;create random coefficients
coeffA = randomn(seed, nfiles)
coeffB = randomn(seed, nfiles)
coeffC = randomn(seed, nfiles)
;populates y with noisy data
for kkk=0ul, nfiles-1 do begin
   y[kkk,*] = coeffA[kkk]*sin(X*coeffB[kkk]) + coeffC[kkk]
   for nnn=0ul, n_points-1 do begin
      y[kkk,nnn] = y[kkk,nnn] + ynoise[nnn]/7
   endfor
endfor


;creates file names
file=strarr(nfiles)

for mmm=0ul, nfiles-1 do begin
   file[mmm] = 'dummyplot'+strtrim(mmm+1,2)+'.data'
endfor


;populates file array with data from x and y arrays and gives each
;file a header and footer
for iii=0ul, n_elements(file)-1 do begin
   openw,lun, file[iii],/get_lun
   printf, lun, 'This is file '+file[iii]
   printf, lun, 'File created on: ', systime(/UTC)+'.'
   for jjj=0ul, n_points-1 do begin
      printf,lun,'     ',x[jjj],'    ',y[iii,jjj]
   endfor
   printf, lun, 'EOF'
   free_lun,lun
endfor
output = y
end
