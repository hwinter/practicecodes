;
;Name: dih_get_goes
;
;Purpose: gets goes data and saves it into a text file
;
;
;
;
;
;
;
;
;
pro dih_get_goes, start_time, end_time, save_name
rd_goes_sdac, stime= start_time ,etime=end_time, tarray=goes_time, yarray=goes_flux, base_ascii=base_ascii
time_str =  atime(goes_time+anytim(base_ascii))
new_time = goes_time - goes_time[0]
real_start = atime(goes_time[0]+anytim(base_ascii))
openw, unit, save_name, /get_lun
printf, unit, real_start
for i=0,n_elements(goes_time)-1 do printf, unit, new_time[i], goes_flux[i,0]
close, unit, /all
end