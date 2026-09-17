**README**
**ANGLE ANALYSIS**

1.
First we filter out all calls registered from outside of the cage+error area of 10cm using  "Filtered_BMR_Location.py" 
INPUT - XYpy.csv" for geophone grid  /// BMR_Seismic amplitudes.xlsx for al calls w/ BMR location  
output -  BMR_seismic_amplitudes_Cage_Filtered260826.xlsx  + Dot maps of BMR location for each call.

2. Spacing_calls.py 
 Insuring Beam independance by applying spacing of 0.5 & 3 sec intervals 



3.BMR Angle Analysis Pipeline

Extracts one beam-direction angle per call, references it to the real intruder position, and runs circular statistics comparing conditions S1 and S2.

Inputs

Spaced-call workbooks (one sheet per R#S# session; needs columns Call_Index, X BMR, Y BMR, Call Time):

BMR_seismic_amplitudes_Cage_Filtered260826_Spaced_500msec.xlsx
BMR_seismic_amplitudes_Cage_Filtered260826_Spaced_3sec.xlsx

Kriging workbooks (one Call_N sheet per call, matched by Call_Index):

R#S#_All_Kriged_Grids.xlsx

Fixed geometry: S1 intruder = (0, 120); S2 intruder = (0, -120). 0 degrees = beam pointing straight at that condition's real intruder.

Outputs

Excel:

Angle_Analysis_Gathered_.xlsx
Detailed_Per_Call_Angles_.xlsx
Circular_Statistics_.xlsx

Plots (PNG + PDF):

Rose_Plot_S1_
Rose_Plot_S2_
Rose_Plot_S1_S2_Combined_
Statistical tests
Circular mean direction, resultant length (R, R-bar), concentration kappa
Rayleigh test (directional preference within a condition)
Von Mises MLE circular regression, likelihood-ratio test (primary S1 vs S2 test)

Dual cosine/sine OLS (supplementary)


Packages

numpy, pandas, matplotlib, scipy, statsmodels, and standard library (os, re, glob).


***KRIGING***
BMR Kriging Pipeline

Interpolates per-call seismic amplitude maps across the microphone array using ordinary kriging, produces individual and mean maps per condition, and exports the interpolated grids to Excel (these feed the angle-analysis pipeline).

Inputs

Amplitude workbook (one sheet per R#S# condition; column 1 = mic number, remaining columns = call IDs):

BMR_seismic_amplitudes_Cage_Filtered260826_Mic_Rows.xlsx

Coordinate file (two columns X, Y, no header; mic 0 added at (0,0) so rows become mics 1-50):

XYpy.csv
Outputs

Per condition, under Kriging//:

Excel:

_All_Kriged_Grids.xlsx (sheet 1 = Mean_Kriged_Grid; then one Call_N sheet per kriged call)

Maps (PNG + PDF):

_Mean_Of_Kriged_Maps
Singles/Kriging_Call (one per call)
Method
Ordinary kriging (spherical variogram) per call, interpolated onto an 80 x 100 grid padded around the mic positions
Calls with fewer than 3 valid (non-zero, finite) mic values are skipped
Mean map = average of the individual kriged grids
Mic-nearest grid cells are bold/bordered in the Excel output


Packages

numpy, pandas, matplotlib, pykrige (OrdinaryKriging), openpyxl, and standard library (os, re, glob).



//Supp//
* "vectored_calls.py"  , pulls out specific beas from a specific chosen spaced calls file and plots a max of 3 chosen beams' BMR beam maxima - Intruder vector. 