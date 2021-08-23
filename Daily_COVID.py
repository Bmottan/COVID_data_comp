from matplotlib import pyplot as plt
import matplotlib.ticker as ticker
from datetime import date
import statistics
import pandas as pd
import requests
from selenium import webdriver
import matplotlib.gridspec as gridspec
import numpy as np


#_____________________________________________________________________________

# Today's date

today = str(date.today())
todayymd = date.today()
todaymdy = todayymd.strftime('%m/%d/%Y')
todaydmy = todayymd.strftime('%d/%m/%Y')
print(todaymdy)

#_____________________________________________________________________________

# Get online data - BRAZIL and PARANA

url = "https://raw.githubusercontent.com/wcota/covid19br/master/cases-brazil-states.csv"

# Test HTTP connection
response = requests.get(url)
if str(response) == "<Response [200]>":
    print("Connection 1 OK. Saving data...") #status code: 200 = OK, successful HTTP request
else:
    print("Connection 1 error." + str(response))
    
# Get Data
htmlText = response.text

# Write CSV file
folder = r'C:\Users\Bruno\Documents\GitHub\COVID_data_comp\Import Data\\'
file2write=open(folder + today + "-BR.csv",'w')
file2write.write(htmlText)
file2write.close()

# Transform data into array

df = pd.read_csv (folder + today + '-BR.csv')


# sort by multiple columns: state and ascending date
df.sort_values(by=['state','date'], inplace=True)


#_____________________________________________________________________________
# BRAZIL
#_____________________________________________________________________________


grouped = df.groupby(df.state)
BR = grouped.get_group("TOTAL")
BR.reset_index(drop=True, inplace=True)

r = len(BR)
c = len(BR.columns)

#Calculate 7 day means - Cases
BRcases = BR.loc[0:r, 'newCases']
BRmeancase = list(range(r))
for x in range(len(BRcases)):
    if x <= 6:
        BRmeancase[x] = BRcases[x]
    else:
        BRmeancase[x] = statistics.mean(BRcases[x-7:x])
BR.insert(len(BR.columns), "7dayMeanCases", BRmeancase, True) 

#Calculate 7 day means - Death
BRdeaths = BR.loc[0:r, 'newDeaths']
BRmeandeath = list(range(r))
for x in range(len(BRdeaths)):
    if x <= 6:
        BRmeandeath[x] = BRdeaths[x]
    else:
        BRmeandeath[x] = statistics.mean(BRdeaths[x-7:x])
BR.insert(len(BR.columns), "7dayMeanDeaths", BRmeandeath, True) 

#Last week diff.:
BRmcasediff = ((BR.loc[r-1, '7dayMeanCases'] - BR.loc[r-8, '7dayMeanCases'])/BR.loc[r-8, '7dayMeanCases'])*100
BRmdeathdiff = ((BR.loc[r-1, '7dayMeanDeaths'] - BR.loc[r-8, '7dayMeanDeaths'])/BR.loc[r-8, '7dayMeanDeaths'])*100

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#Initiate plot

# Define plot space
fig = plt.figure(1, figsize=(48, 20), dpi=300)
fig.suptitle("COVID data as of "+ todaymdy, fontsize =30, fontweight='bold')


#remember, gridspec is rows, then columns
gs = gridspec.GridSpec(5,8, height_ratios=[1,1,1,0.4,1])
gs.update(wspace=0.45, hspace=0.0)

#box
props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



# Define x and y axes - Suplot 1case - BRAZIL

y1 = fig.add_subplot(gs[0,4:6])

plt.plot(BR['date'], BR['totalCases'], color = 'blue', linestyle='-', alpha=0.8)
# Set plot title and axes labels

y1.set_ylabel('Total Cases', loc='center', fontsize=18)
y1.xaxis.set_major_locator(ticker.MultipleLocator(30))
y1.set_title('Brazil', fontsize=25, fontweight='bold')

recent = '\n'.join(("Total cases: {:,}".format( BR.loc[r-1, 'totalCases'] ),
    BR.loc[r-1, 'date']))
y1.text(0.05, 0.95, recent, transform=y1.transAxes, fontsize=14,
        verticalalignment='top', bbox=props)

plt.minorticks_on()
y1.set_xticklabels([])
y1.yaxis.label.set_color('blue')
y1.tick_params(axis='x', direction='in',which='minor', length=5, 
                bottom=True, top=False, left=False, right=False)
y1.tick_params(axis='x', direction='in',which='major', length=10, 
                bottom=True, top=False, left=False, right=False)
y1.tick_params(axis='y', colors='blue', direction='out',which='minor', length=5, 
                bottom=False, top=False, left=True, right=False)
y1.tick_params(axis='y', colors='blue', direction='out',which='major', length=10, 
                bottom=False, top=False, left=True, right=False, labelsize=14)
plt.grid(which='major', axis='both', alpha=0.1)

#sci notation
y1.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
#sci notation int location
y1.get_yaxis().get_offset_text().set_visible(False)
ax_max = max(y1.get_yticks())
exponent_axis = np.floor(np.log10(ax_max)).astype(int)
y1.annotate(r'$\times$10$^{%i}$'%(exponent_axis),  rotation = 90,
             xy=(0.01, .85), xycoords='axes fraction', fontsize=14, color='blue')

plt.arrow(300, 1.1*ax_max/3, -100, 0, color='blue',head_width=ax_max/30, head_length=10)


# Define x and y axes - Suplot 1death
y2 = plt.twinx()
y2.plot(BR['date'], BR['deaths'], color = 'red', linestyle='-.', alpha=0.8)
# Set plot title and axes labels

y2.xaxis.set_major_locator(ticker.MultipleLocator(30))
y2.set_ylabel('Total Deaths', loc='center', fontsize=18)
recent = '\n'.join(('Total deaths: {:,}'.format(BR.loc[r-1, 'deaths']),
    BR.loc[r-1, 'date']))
y2.text(0.95, 0.05, recent, transform=y2.transAxes, fontsize=14,
        verticalalignment='bottom',  horizontalalignment='right', bbox=props)

y2.yaxis.label.set_color('red')
y2.set_ylim([-0.5e5, 7e5])
plt.minorticks_on()
y2.tick_params(axis='y', colors='red', direction='out',which='minor', length=5, 
                bottom=False, top=False, left=False, right=True)
y2.tick_params(axis='y', colors='red', direction='out',which='major', length=10, 
                bottom=False, top=False, left=False, right=True, labelsize=14)


#sci notation
y2.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
#sci notation int location
y1.get_yaxis().get_offset_text().set_visible(False)
y2.get_yaxis().get_offset_text().set_visible(False)
ax_max = max(y2.get_yticks())
exponent_axis = np.floor(np.log10(ax_max)).astype(int)
y2.annotate(r'$\times$10$^{%i}$'%(exponent_axis), rotation = 90,
             xy=(0.975, .85), xycoords='axes fraction', fontsize=14, color='red')

plt.arrow(370, ax_max/3, 100, 0, color='red',head_width=ax_max/30, head_length=10)




# Define x and y axes - Suplot 2necase
y1 = fig.add_subplot(gs[1,4:6])
plt.bar(BR['date'], BR['newCases'], color = 'lightblue')
# Set plot title and axes labels

y1.set_ylabel('New Cases', loc='center', fontsize=18)
y1.xaxis.set_major_locator(ticker.MultipleLocator(30))

plt.plot(BR['date'], BR['7dayMeanCases'], color = 'magenta')

recent = '\n'.join((
    'New cases: {:,}'.format(BR.loc[r-1, 'newCases']),
    'Last week diff.: %+.2f'% BRmcasediff + '%',
    BR.loc[r-1, 'date']))
y1.text(0.05, 0.95, recent, transform=y1.transAxes, fontsize=14,
        verticalalignment='top', bbox=props)
plt.minorticks_on()
y1.set_xticklabels([])
y1.yaxis.label.set_color('blue')
y1.tick_params(axis='x', direction='in',which='minor', length=5, 
                bottom=True, top=False, left=False, right=False)
y1.tick_params(axis='x', direction='in',which='major', length=10, 
                bottom=True, top=False, left=False, right=False)
y1.tick_params(axis='y', colors='blue', direction='out',which='minor', length=5, 
                bottom=False, top=False, left=True, right=False)
y1.tick_params(axis='y', colors='blue', direction='out',which='major', length=10, 
                bottom=False, top=False, left=True, right=False, labelsize=14)
plt.grid(which='major', axis='both', alpha=0.1)

y1.set_ylim([0, 1e5])

#sci notation
y1.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
#sci notation int location
y1.get_yaxis().get_offset_text().set_visible(False)
ax_max = max(y1.get_yticks())
exponent_axis = np.floor(np.log10(ax_max)).astype(int)
y1.annotate(r'$\times$10$^{%i}$'%(exponent_axis),  rotation = 90,
             xy=(0.01, .85), xycoords='axes fraction', fontsize=14, color='blue')





# Define x and y axes - Suplot 3newdeath
y1 = fig.add_subplot(gs[2,4:6])
y1.bar(BR['date'], BR['newDeaths'], color = 'pink')
# Set plot title and axes labels
y1.set_ylabel('New Deaths', loc='center', fontsize=18)
y1.xaxis.set_major_locator(ticker.MultipleLocator(30))
plt.setp(y1.get_xticklabels(), rotation = 90)

y1.plot(BR['date'], BR['7dayMeanDeaths'], color = 'magenta')

recent = '\n'.join((
    'New deaths: {:,}'.format(BR.loc[r-1, 'newDeaths']),
    'Last week diff.: %+.2f'% BRmdeathdiff + '%',
    BR.loc[r-1, 'date']))
y1.text(0.05, 0.95, recent, transform=y1.transAxes, fontsize=14,
        verticalalignment='top', bbox=props)
y1.yaxis.label.set_color('red')

plt.minorticks_on()
y1.tick_params(axis='x', direction='inout',which='minor', length=5, 
                bottom=True, top=False, left=False, right=False)
y1.tick_params(axis='x', direction='inout',which='major', length=10, 
                bottom=True, top=False, left=False, right=False,labelsize=14)
y1.tick_params(axis='y', colors='red', direction='out',which='minor', length=5, 
                bottom=False, top=False, left=True, right=False)
y1.tick_params(axis='y', colors='red', direction='out',which='major', length=10, 
                bottom=False, top=False, left=True, right=False, labelsize=14)
plt.grid(which='major', axis='both', alpha=0.1)

#sci notation
y1.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
#sci notation int location
y1.get_yaxis().get_offset_text().set_visible(False)
ax_max = max(y1.get_yticks())
exponent_axis = np.floor(np.log10(ax_max)).astype(int)
y1.annotate(r'$\times$10$^{%i}$'%(exponent_axis),  rotation = 90,
             xy=(0.01, .85), xycoords='axes fraction', fontsize=14, color='red')

#percentages pop
BRpop = 211000000
marks = [BRpop*0.1, BRpop*0.2,BRpop*0.3, BRpop*0.4, BRpop*0.5, BRpop*0.6, BRpop*0.7]
marksv1 = []
marksv2 = []
c = 0
for x in BR.index:
    for y in range(len(marks)):
        if marks[c]<=BR.at[x,'vaccinated'] and marks[c]>=BR.at[x-1,'vaccinated'] :
            mark=x
            marksv1.append(mark)
            c=c+1
c=0
for x in BR.index:
    for y in range(len(marks)):
        if marks[c]<=BR.at[x,'vaccinated_second'] and marks[c]>=BR.at[x-1,'vaccinated_second'] :
            mark=x
            marksv2.append(mark)
            c=c+1
txt=['10%','20%','30%','40%','50%','60%','70%']
color=['']

inivac = 346 #inicio da vacinação
#%%
#13/06/20 a 17/08: bandeira laranja
for vac in range(len(marksv1)):
    if vac == 0:
        delta = marksv1[vac]-inivac+1
        plt.arrow(inivac,ax_max/4, delta, 0, color='blue',linewidth=20,linestyle='-', alpha=0.2, head_length=0)
    elif vac < len(marksv1)-1:
        delta = marksv1[vac+1]-marksv1[vac]+1
        plt.arrow(marksv1[vac],ax_max/4, delta, 0, color='orange',linewidth=20,linestyle='-', alpha=0.2, head_length=0)


vacin = BR['vaccinated_second']/BRpop

left, bottom, width, height = [0, 0.5, 1, 0.2]
ax2 = fig.add_axes([left, bottom, width, height])
plt.imshow((BR['date'].index, vacin), cmap='jet_r')


from matplotlib.collections import LineCollection
lc = LineCollection(BR['7dayMeanDeaths'], cmap='viridis')
# Set the values used for colormapping
lc.set_array(vacin)
lc.set_linewidth(2)
line = axs[0].add_collection(lc)

#%%

# Define x and y axes - Suplot 4vax
y1 = fig.add_subplot(gs[4,4:6])
y1.plot(BR['date'], BR['vaccinated'], color = 'orange')
y1.plot(BR['date'], BR['vaccinated_second'], color = 'green')
# Set plot title and axes labels

#percentages text

txt=['10%','20%','30%','40%','50%','60%','70%']
for i in range(len(marksv1)):
    plt.text(marksv1[i], marks[i], txt[i])
for i in range(len(marksv2)):
    plt.text(marksv2[i], marks[i], txt[i])


y1.set_xlabel('Date', loc='center', fontsize=18)
y1.set_ylabel('Vaccinated', loc='center', fontsize=18)
y1.xaxis.set_major_locator(ticker.MultipleLocator(14))
plt.setp(y1.get_xticklabels(), rotation = 90)

pop1 = (BR.loc[r-1, 'vaccinated']/BRpop)*100
pop2 = (BR.loc[r-1, 'vaccinated_second']/BRpop)*100
recent = '\n'.join(('1st dose: {:,.0f}'.format(BR.loc[r-1, 'vaccinated']),
                    'Full vax: {:,.0f}'.format(BR.loc[r-1, 'vaccinated_second']),
                    'Pop. 1st: %.2f'% pop1 + '%',
                    'Pop. full vax: %.2f'% pop2 + '%',
    BR.loc[r-1, 'date']))
y1.text(0.05, 0.95, recent, transform=y1.transAxes, fontsize=14,
        verticalalignment='top', bbox=props)
plt.minorticks_on()
y1.yaxis.label.set_color('green')
y1.tick_params(axis='x', direction='inout',which='minor', length=5, 
                bottom=True, top=False, left=False, right=False)
y1.tick_params(axis='x', direction='inout',which='major', length=10, 
                bottom=True, top=False, left=False, right=False,labelsize=14)
y1.tick_params(axis='y', colors='green', direction='out',which='minor', length=5, 
                bottom=False, top=False, left=True, right=False)
y1.tick_params(axis='y', colors='green', direction='out',which='major', length=10, 
                bottom=False, top=False, left=True, right=False, labelsize=14)
plt.grid(which='major', axis='both', alpha=0.1)

#sci notation
y1.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
#sci notation int location
y1.get_yaxis().get_offset_text().set_visible(False)
ax_max = max(y1.get_yticks())
exponent_axis = np.floor(np.log10(ax_max)).astype(int)
y1.annotate(r'$\times$10$^{%i}$'%(exponent_axis),  rotation = 90,
             xy=(0.01, .85), xycoords='axes fraction', fontsize=14, color='green')





BRflag = plt.imread(r'C:\Users\Bruno\Desktop\COVID19\Bandeira\Flag_Brazil.png')
newax = fig.add_axes([0.593, 0.86, 0.06, 0.06], zorder=1)
newax.imshow(BRflag, alpha=0.5)
newax.axis('off')


print('Brazil data - complete.')



#_____________________________________________________________________________
# PARANA
#_____________________________________________________________________________



grouped = df.groupby(df.state)
PR = grouped.get_group("PR")
PR.reset_index(drop=True, inplace=True)

r = len(PR)
c = len(PR.columns)

#Calculate 7 day means - Cases
PRcases = PR.loc[0:r, 'newCases']
PRmeancase = list(range(r))
for x in range(len(PRcases)):
    if x <= 6:
        PRmeancase[x] = PRcases[x]
    else:
        PRmeancase[x] = statistics.mean(PRcases[x-7:x])
PR.insert(len(PR.columns), "7dayMeanCases", PRmeancase, True) 

#Calculate 7 day means - Death
PRdeaths = PR.loc[0:r, 'newDeaths']
PRmeandeath = list(range(r))
for x in range(len(PRdeaths)):
    if x <= 6:
        PRmeandeath[x] = PRdeaths[x]
    else:
        PRmeandeath[x] = statistics.mean(PRdeaths[x-7:x])
PR.insert(len(PR.columns), "7dayMeanDeaths", PRmeandeath, True) 

#Last week diff.:
PRmcasediff = ((PR.loc[r-1, '7dayMeanCases'] - PR.loc[r-8, '7dayMeanCases'])/PR.loc[r-8, '7dayMeanCases'])*100
PRmdeathdiff = ((PR.loc[r-1, '7dayMeanDeaths'] - PR.loc[r-8, '7dayMeanDeaths'])/PR.loc[r-8, '7dayMeanDeaths'])*100


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Define x and y axes - Suplot 1case - PARANA

y1 = fig.add_subplot(gs[0,2:4])

y1.plot(PR['date'], PR['totalCases'], color = 'blue', linestyle='-', alpha=0.8)
# Set plot title and axes labels

y1.set_ylabel('Total Cases', loc='center',fontsize=18)
y1.xaxis.set_major_locator(ticker.MultipleLocator(30))
y1.set_title('Paraná', fontsize=25, fontweight='bold')

recent = '\n'.join(('Total cases: {:,}'.format(PR.loc[r-1, 'totalCases']),
    PR.loc[r-1, 'date']))
y1.text(0.05, 0.95, recent, transform=y1.transAxes, fontsize=14,
        verticalalignment='top', bbox=props)

plt.minorticks_on()
y1.set_xticklabels([])
y1.yaxis.label.set_color('blue')
y1.tick_params(axis='x', direction='in',which='minor', length=5, 
                bottom=True, top=False, left=False, right=False)
y1.tick_params(axis='x', direction='in',which='major', length=10, 
                bottom=True, top=False, left=False, right=False)
y1.tick_params(axis='y', colors='blue', direction='out',which='minor', length=5, 
                bottom=False, top=False, left=True, right=False)
y1.tick_params(axis='y', colors='blue', direction='out',which='major', length=10, 
                bottom=False, top=False, left=True, right=False, labelsize=14)
plt.grid(which='major', axis='both', alpha=0.1)

#sci notation
y1.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
#sci notation int location
y1.get_yaxis().get_offset_text().set_visible(False)
ax_max = max(y1.get_yticks())
exponent_axis = np.floor(np.log10(ax_max)).astype(int)
y1.annotate(r'$\times$10$^{%i}$'%(exponent_axis),  rotation = 90,
             xy=(0.01, .85), xycoords='axes fraction', fontsize=14, color='blue')

plt.arrow(300, 1.2*ax_max/3, -100, 0, color='blue',head_width=ax_max/30, head_length=10)


# Define x and y axes - Suplot 1death
y2 = y1.twinx()
y2.plot(PR['date'], PR['deaths'], color = 'red', linestyle='-.', alpha=0.8)
# Set plot title and axes labels

y2.xaxis.set_major_locator(ticker.MultipleLocator(30))

recent = '\n'.join(('Total deaths: {:,}'.format(PR.loc[r-1, 'deaths']),
    PR.loc[r-1, 'date']))
y2.text(0.95, 0.05, recent, transform=y1.transAxes, fontsize=14,
        verticalalignment='bottom',  horizontalalignment='right', bbox=props)

y2.set_ylabel('Total Deaths', loc='center',fontsize=18)

y2.yaxis.label.set_color('red')
y2.set_ylim([-0.2e4, 4e4])
plt.minorticks_on()
y2.tick_params(axis='y', colors='red', direction='out',which='minor', length=5, 
                bottom=False, top=False, left=False, right=True)
y2.tick_params(axis='y', colors='red', direction='out',which='major', length=10, 
                bottom=False, top=False, left=False, right=True,labelsize=14)
y2.ticklabel_format(axis='y', style='sci', scilimits=(0,0))

#sci notation
y2.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
#sci notation int location
y1.get_yaxis().get_offset_text().set_visible(False)
y2.get_yaxis().get_offset_text().set_visible(False)
ax_max = max(y2.get_yticks())
exponent_axis = np.floor(np.log10(ax_max)).astype(int)
y2.annotate(r'$\times$10$^{%i}$'%(exponent_axis), rotation = 90,
             xy=(0.975, .85), xycoords='axes fraction', fontsize=14, color='red')

plt.arrow(370, ax_max/3, 100, 0, color='red',head_width=ax_max/30, head_length=10)




# Define x and y axes - Suplot 2newcases
y1 = fig.add_subplot(gs[1,2:4])
y1.bar(PR['date'], PR['newCases'], color = 'lightblue')
# Set plot title and axes labels

y1.set_ylabel('New Cases', loc='center',fontsize=18)
y1.xaxis.set_major_locator(ticker.MultipleLocator(30))

y1.plot(PR['date'], PR['7dayMeanCases'], color = 'magenta')
y1.set_ylim([0, 1.4e4])

recent = '\n'.join((
    'New cases: {:,}'.format(PR.loc[r-1, 'newCases']),
    'Last week diff.: %+.2f'% PRmcasediff + '%',
    PR.loc[r-1, 'date']))
y1.text(0.05, 0.95, recent, transform=y1.transAxes, fontsize=14,
        verticalalignment='top', bbox=props)
plt.minorticks_on()
y1.set_xticklabels([])
y1.yaxis.label.set_color('blue')
y1.tick_params(axis='x', direction='in',which='minor', length=5, 
                bottom=True, top=False, left=False, right=False)
y1.tick_params(axis='x', direction='in',which='major', length=10, 
                bottom=True, top=False, left=False, right=False)
y1.tick_params(axis='y', colors='blue', direction='out',which='minor', length=5, 
                bottom=False, top=False, left=True, right=False)
y1.tick_params(axis='y', colors='blue', direction='out',which='major', length=10, 
                bottom=False, top=False, left=True, right=False, labelsize=14)
plt.grid(which='major', axis='both', alpha=0.1)
y1.ticklabel_format(axis='y', style='sci', scilimits=(0,0))

#sci notation
y1.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
#sci notation int location
y1.get_yaxis().get_offset_text().set_visible(False)
ax_max = max(y1.get_yticks())
exponent_axis = np.floor(np.log10(ax_max)).astype(int)
y1.annotate(r'$\times$10$^{%i}$'%(exponent_axis),  rotation = 90,
             xy=(0.01, .85), xycoords='axes fraction', fontsize=14, color='blue')




# Define x and y axes - Suplot 3newdeaths
y1 = fig.add_subplot(gs[2,2:4])
y1.bar(PR['date'], PR['newDeaths'], color = 'pink')
# Set plot title and axes labels
y1.set_ylabel('New Deaths', loc='center',fontsize=18)
y1.xaxis.set_major_locator(ticker.MultipleLocator(30))
plt.setp(y1.get_xticklabels(), rotation = 90)

y1.plot(PR['date'], PR['7dayMeanDeaths'], color = 'magenta')
y1.set_ylim([0, 350])

recent = '\n'.join((
    'New deaths: {:,}'.format(PR.loc[r-1, 'newDeaths']),
    'Last week diff.: %+.2f'% PRmdeathdiff + '%',
    PR.loc[r-1, 'date']))
y1.text(0.05, 0.95, recent, transform=y1.transAxes, fontsize=14,
        verticalalignment='top', bbox=props)
y1.tick_params(axis='x', direction='inout',which='minor', length=5, 
                bottom=True, top=False, left=False, right=False)
y1.tick_params(axis='x', direction='inout',which='major', length=10, 
                bottom=True, top=False, left=False, right=False,labelsize=14)
y1.yaxis.label.set_color('red')
plt.minorticks_on()
y1.tick_params(axis='y', colors='red', direction='out',which='minor', length=5, 
                bottom=False, top=False, left=True, right=False)
y1.tick_params(axis='y', colors='red', direction='out',which='major', length=10, 
                bottom=False, top=False, left=True, right=False,labelsize=14)
plt.grid(which='major', axis='both', alpha=0.1)
y1.ticklabel_format(axis='y', style='sci', scilimits=(0,0))

#sci notation
y1.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
#sci notation int location
y1.get_yaxis().get_offset_text().set_visible(False)
ax_max = max(y1.get_yticks())
exponent_axis = np.floor(np.log10(ax_max)).astype(int)
y1.annotate(r'$\times$10$^{%i}$'%(exponent_axis),  rotation = 90,
             xy=(0.01, .85), xycoords='axes fraction', fontsize=14, color='red')




# Define x and y axes - Suplot 4vax
y1 = fig.add_subplot(gs[4,2:4])
y1.plot(PR['date'], PR['vaccinated'], color = 'orange')
y1.plot(PR['date'], PR['vaccinated_second'], color = 'green')
# Set plot title and axes labels

#percentages text
PRpop = 11080000
marks = [PRpop*0.1, PRpop*0.2,PRpop*0.3, PRpop*0.4, PRpop*0.5, PRpop*0.6, PRpop*0.7]
marksv1 = []
marksv2 = []
c = 0
for x in PR.index:
    for y in range(len(marks)):
        if marks[c]<=PR.at[x,'vaccinated'] and marks[c]>=PR.at[x-1,'vaccinated'] :
            mark=x
            marksv1.append(mark)
            c=c+1
c=0
for x in PR.index:
    for y in range(len(marks)):
        if marks[c]<=PR.at[x,'vaccinated_second'] and marks[c]>=PR.at[x-1,'vaccinated_second'] :
            mark=x
            marksv2.append(mark)
            c=c+1
txt=['10%','20%','30%','40%','50%','60%','70%']
for i in range(len(marksv1)):
    plt.text(marksv1[i], marks[i], txt[i])
for i in range(len(marksv2)):
    plt.text(marksv2[i], marks[i], txt[i])



#y1.set(title = " ",
#       xlabel = "Date",
#       ylabel = "Vaccinated")
y1.set_xlabel('Date', loc='center',fontsize=18)
y1.set_ylabel('Vaccinated', loc='center',fontsize=18)
y1.xaxis.set_major_locator(ticker.MultipleLocator(14))
plt.setp(y1.get_xticklabels(), rotation = 90)

pop1 = (PR.loc[r-1, 'vaccinated']/PRpop)*100
pop2 = (PR.loc[r-1, 'vaccinated_second']/PRpop)*100
recent = '\n'.join(('1st dose: {:,.0f}'.format(PR.loc[r-1, 'vaccinated']),
                    'Full vax: {:,.0f}'.format(PR.loc[r-1, 'vaccinated_second']),
                    'Pop. 1st: %.2f'% pop1 + '%',
                    'Pop. full vax: %.2f'% pop2 + '%',
    PR.loc[r-1, 'date']))
y1.text(0.05, 0.95, recent, transform=y1.transAxes, fontsize=14,
        verticalalignment='top', bbox=props)
plt.minorticks_on()
y1.yaxis.label.set_color('green')
y1.tick_params(axis='x', direction='inout',which='minor', length=5, 
                bottom=True, top=False, left=False, right=False)
y1.tick_params(axis='x', direction='inout',which='major', length=10, 
                bottom=True, top=False, left=False, right=False,labelsize=14)
y1.tick_params(axis='y', colors='green', direction='out',which='minor', length=5, 
                bottom=False, top=False, left=True, right=False)
y1.tick_params(axis='y', colors='green', direction='out',which='major', length=10, 
                bottom=False, top=False, left=True, right=False,labelsize=14)
plt.grid(which='major', axis='both', alpha=0.1)
y1.ticklabel_format(axis='y', style='sci', scilimits=(0,0))

#sci notation
y1.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
#sci notation int location
y1.get_yaxis().get_offset_text().set_visible(False)
ax_max = max(y1.get_yticks())
exponent_axis = np.floor(np.log10(ax_max)).astype(int)
y1.annotate(r'$\times$10$^{%i}$'%(exponent_axis),  rotation = 90,
             xy=(0.01, .85), xycoords='axes fraction', fontsize=14, color='green')



PRflag = plt.imread(r'C:\Users\Bruno\Desktop\COVID19\Bandeira\Flag_Paraná.png')
newax = fig.add_axes([0.345, 0.86, 0.06, 0.06], zorder=1)
newax.imshow(PRflag, alpha=0.5)
newax.axis('off')




print('Paraná data - complete.')





#_____________________________________________________________________________
# Massachusetts-USA
#_____________________________________________________________________________


# Get online data


url = "https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv"

# Test HTTP connection
response = requests.get(url)
if str(response) == "<Response [200]>":
    print("Connection 2 OK. Saving data...") #status code: 200 = OK, successful HTTP request
else:
    print("Connection 2 error." + str(response))


# Get Data
htmlText = response.text


# Write CSV file
file2write=open(folder + today + "USA.csv",'w')
file2write.write(htmlText)
file2write.close()

# Transform data into array
import pandas as pd
df = pd.read_csv (folder + today + 'USA.csv')
#print (df)

# sort by multiple columns: state and ascending date
df.sort_values(by=['state','date'], inplace=True)
#print(df)


grouped = df.groupby(df.state)
MA = grouped.get_group("Massachusetts")
MA.reset_index(drop=True, inplace=True)

r = len(MA)
c = len(MA.columns)

#Calculate new Cases and 7 day mean
MAcases = MA.loc[0:r, 'cases']
MAmeancase = list(range(r))
MAnewcases = list(range(r))

for x in range(len(MAcases)):
    if x == 0:
        MAnewcases[x] = MAcases[x]
    else:
        MAnewcases[x] = MAcases[x]-MAcases[x-1]
MA.insert(len(MA.columns), "newCases", MAnewcases, True) 

for x in range(len(MAnewcases)):
    if x <= 6:
        MAmeancase[x] = MAnewcases[x]
    else:
        MAmeancase[x] = statistics.mean(MAnewcases[x-7:x])
MA.insert(len(MA.columns), "7dayMeanCases", MAmeancase, True) 
   

#Calculate 7 day means - Death
MAdeaths = MA.loc[0:r, 'deaths']
MAmeandeath = list(range(r))
MAnewdeaths = list(range(r))

for x in range(len(MAdeaths)):
    if x == 0:
        MAnewdeaths[x] = MAdeaths[x]
    else:
        MAnewdeaths[x] = MAdeaths[x]-MAdeaths[x-1]
MA.insert(len(MA.columns), "newDeaths", MAnewdeaths, True)

for x in range(len(MAnewdeaths)):
    if x <= 6:
        MAmeandeath[x] = MAnewdeaths[x]
    else:
        MAmeandeath[x] = statistics.mean(MAnewdeaths[x-7:x])
MA.insert(len(MA.columns), "7dayMeanDeaths", MAmeandeath, True) 

#Last week diff.:
MAmdeathdiff = ((MA.loc[r-1, '7dayMeanDeaths'] - MA.loc[r-8, '7dayMeanDeaths'])/MA.loc[r-8, '7dayMeanDeaths'])*100
MAmcasediff = ((MA.loc[r-1, '7dayMeanCases'] - MA.loc[r-8, '7dayMeanCases'])/MA.loc[r-8, '7dayMeanCases'])*100
 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Define x and y axes - Suplot 1cases
y1 = fig.add_subplot(gs[0,6:8])
y1.plot(MA['date'], MA['cases'], color = 'blue',  linestyle='-', alpha=0.8)
# Set plot title and axes labels

y1.set_ylabel('Total Cases', loc='center',fontsize=18)
y1.xaxis.set_major_locator(ticker.MultipleLocator(30))
y1.set_title('Massachusetts', fontsize=25, fontweight='bold')

recent = '\n'.join(('Total cases: {:,}'.format(MA.loc[r-1, 'cases']),
    MA.loc[r-1, 'date']))
y1.text(0.05, 0.95, recent, transform=y1.transAxes, fontsize=14,
        verticalalignment='top', bbox=props)

plt.minorticks_on()
y1.set_xticklabels([])
y1.yaxis.label.set_color('blue')
y1.tick_params(axis='x', direction='in',which='minor', length=5, 
                bottom=True, top=False, left=False, right=False)
y1.tick_params(axis='x', direction='in',which='major', length=10, 
                bottom=True, top=False, left=False, right=False)
y1.tick_params(axis='y', colors='blue', direction='out',which='minor', length=5, 
                bottom=False, top=False, left=True, right=False)
y1.tick_params(axis='y', colors='blue', direction='out',which='major', length=10, 
                bottom=False, top=False, left=True, right=False, labelsize=14)
plt.grid(which='major', axis='both', alpha=0.1)

#sci notation
y1.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
#sci notation int location
y1.get_yaxis().get_offset_text().set_visible(False)
ax_max = max(y1.get_yticks())
exponent_axis = np.floor(np.log10(ax_max)).astype(int)
y1.annotate(r'$\times$10$^{%i}$'%(exponent_axis),  rotation = 90,
             xy=(0.01, .85), xycoords='axes fraction', fontsize=14, color='blue')

plt.arrow(300, ax_max/3, -100, 0, color='blue',head_width=ax_max/30, head_length=10)



# Define x and y axes - Suplot 1death
y2 = y1.twinx()
y2.plot(MA['date'], MA['deaths'], color = 'red', linestyle='-.', alpha=0.8)
# Set plot title and axes labels

y2.xaxis.set_major_locator(ticker.MultipleLocator(30))
y2.set_ylabel('Total Deaths', loc='center',fontsize=18)
recent = '\n'.join(('Total deaths: {:,}'.format(MA.loc[r-1, 'deaths']),
    MA.loc[r-1, 'date']))
y2.text(0.95, 0.05, recent, transform=y1.transAxes, fontsize=14,
        verticalalignment='bottom',  horizontalalignment='right', bbox=props)

y2.yaxis.label.set_color('red')
y2.set_ylim([-0.1e4, 2e4])
plt.minorticks_on()
y2.tick_params(axis='y', colors='red', direction='out',which='minor', length=5, 
                bottom=False, top=False, left=False, right=True)
y2.tick_params(axis='y', colors='red', direction='out',which='major', length=10, 
                bottom=False, top=False, left=False, right=True, labelsize=14)

#sci notation
y2.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
#sci notation int location
y1.get_yaxis().get_offset_text().set_visible(False)
y2.get_yaxis().get_offset_text().set_visible(False)
ax_max = max(y2.get_yticks())
exponent_axis = np.floor(np.log10(ax_max)).astype(int)
y2.annotate(r'$\times$10$^{%i}$'%(exponent_axis), rotation = 90,
             xy=(0.975, .85), xycoords='axes fraction', fontsize=14, color='red')

plt.arrow(350, 2*ax_max/3, 100, 0, color='red',head_width=ax_max/30, head_length=10)




# Define x and y axes - Suplot 2 new cases
y1 = fig.add_subplot(gs[1,6:8])
y1.bar(MA['date'], MA['newCases'], color = 'lightblue')
# Set plot title and axes labels

y1.set_ylabel('New Cases', loc='center',fontsize=18)
y1.xaxis.set_major_locator(ticker.MultipleLocator(30))

y1.plot(MA['date'], MA['7dayMeanCases'], color = 'magenta')
y1.set_ylim([0,8000])

recent = '\n'.join((
    'New cases: {:,}'.format(MA.loc[r-1, 'newCases']),
    'Last week diff.: %+.2f'% MAmcasediff + '%',
    MA.loc[r-1, 'date']))
y1.text(0.05, 0.95, recent, transform=y1.transAxes, fontsize=14,
        verticalalignment='top', bbox=props)

plt.minorticks_on()
y1.set_xticklabels([])
y1.yaxis.label.set_color('blue')
y1.tick_params(axis='x', direction='in',which='minor', length=5, 
                bottom=True, top=False, left=False, right=False)
y1.tick_params(axis='x', direction='in',which='major', length=10, 
                bottom=True, top=False, left=False, right=False)
y1.tick_params(axis='y', colors='blue', direction='out',which='minor', length=5, 
                bottom=False, top=False, left=True, right=False)
y1.tick_params(axis='y', colors='blue', direction='out',which='major', length=10, 
                bottom=False, top=False, left=True, right=False, labelsize=14)
plt.grid(which='major', axis='both', alpha=0.1)

#sci notation
y1.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
#sci notation int location
y1.get_yaxis().get_offset_text().set_visible(False)
ax_max = max(y1.get_yticks())
exponent_axis = np.floor(np.log10(ax_max)).astype(int)
y1.annotate(r'$\times$10$^{%i}$'%(exponent_axis),  rotation = 90,
             xy=(0.01, .85), xycoords='axes fraction', fontsize=14, color='blue')




# Define x and y axes - Suplot 3 new deaths
y1 = fig.add_subplot(gs[2,6:8])
y1.bar(MA['date'], MA['newDeaths'], color = 'pink')
# Set plot title and axes labels
y1.set_ylabel('New Deaths', loc='center',fontsize=18)
y1.xaxis.set_major_locator(ticker.MultipleLocator(30))
plt.setp(y1.get_xticklabels(), rotation = 90)

y1.plot(MA['date'], MA['7dayMeanDeaths'], color = 'magenta')
y1.set_ylim([0,250])

recent = '\n'.join((
    'New deaths: {:,}'.format(MA.loc[r-1, 'newDeaths']),
    'Last week diff.: %+.2f'% MAmdeathdiff + '%',
    MA.loc[r-1, 'date']))
y1.text(0.05, 0.95, recent, transform=y1.transAxes, fontsize=14,
        verticalalignment='top', bbox=props)
plt.minorticks_on()
y1.yaxis.label.set_color('red')
y1.tick_params(axis='x', direction='inout',which='minor', length=5, 
                bottom=True, top=False, left=False, right=False)
y1.tick_params(axis='x', direction='inout',which='major', length=10, 
                bottom=True, top=False, left=False, right=False,labelsize=14)
y1.tick_params(axis='y', colors='red', direction='out',which='minor', length=5, 
                bottom=False, top=False, left=True, right=False)
y1.tick_params(axis='y', colors='red', direction='out',which='major', length=10, 
                bottom=False, top=False, left=True, right=False, labelsize=14)
plt.grid(which='major', axis='both', alpha=0.1)

#sci notation
y1.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
#sci notation int location
y1.get_yaxis().get_offset_text().set_visible(False)
ax_max = max(y1.get_yticks())
exponent_axis = np.floor(np.log10(ax_max)).astype(int)
y1.annotate(r'$\times$10$^{%i}$'%(exponent_axis),  rotation = 90,
             xy=(0.01, .85), xycoords='axes fraction', fontsize=14, color='red')




#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#Massachusetts-vaccine

# Get online data


url = "https://raw.githubusercontent.com/govex/COVID-19/master/data_tables/vaccine_data/us_data/time_series/vaccine_data_us_timeline.csv"

# Test HTTP connection
response = requests.get(url)
if str(response) == "<Response [200]>":
    print("Connection 2.1 OK. Saving data...") #status code: 200 = OK, successful HTTP request
else:
    print("Connection 2.1 error." + str(response))


# Get Data
htmlText = response.text


# Write CSV file
file2write=open(folder+today+"USAvax.csv",'w')
file2write.write(htmlText)
file2write.close()

# Transform data into array
df = pd.read_csv (folder+today+'USAvax.csv')
#print (df)

# sort by multiple columns: state and ascending date
df.sort_values(by=['Province_State','Vaccine_Type','Date'], inplace=True)
#print(df)



grouped = df.groupby(df.Province_State)
MA = grouped.get_group("Massachusetts")
MA = MA.drop(['FIPS','Country_Region','Lat','Long_','Combined_Key'], axis=1)

grouped = MA.groupby(df.Vaccine_Type)
MAallvax = grouped.get_group("All")
MAallvax.reset_index(drop=True, inplace=True)
MAJanssen = grouped.get_group("Janssen")
MAJanssen.reset_index(drop=True, inplace=True)


MAvax = pd.DataFrame(columns = ['1stdose','Fullvax'])

cont = 0
for x in MAallvax.index:
    if MAallvax.at[x,'Date']==MAJanssen.at[cont,'Date'] and pd.isna(MAJanssen.at[cont,'Stage_One_Doses'])!=True:
        MAvax.at[x,'1stdose'] = MAallvax.at[x,'Stage_One_Doses']-MAJanssen.at[cont,'Stage_One_Doses']
        MAvax.at[x,'Fullvax'] = MAallvax.at[x,'Stage_Two_Doses']+MAJanssen.at[cont,'Stage_One_Doses']
        cont = cont+1
    elif MAallvax.at[x,'Date']==MAJanssen.at[cont,'Date'] and pd.isna(MAJanssen.at[cont,'Stage_One_Doses'])==True:
        MAvax.at[x,'1stdose'] = MAallvax.at[x,'Stage_One_Doses']-MAJanssen.at[cont,'Doses_admin']
        MAvax.at[x,'Fullvax'] = MAallvax.at[x,'Stage_Two_Doses']+MAJanssen.at[cont,'Doses_admin']
        cont = cont+1
    else:
        MAvax.at[x,'1stdose'] = MAallvax.at[x,'Stage_One_Doses']
        MAvax.at[x,'Fullvax'] = MAallvax.at[x,'Stage_Two_Doses']



r = len(MAvax)
c = len(MAvax.columns)

#___________________________________


# Define x and y axes - Suplot 5
y1 = fig.add_subplot(gs[4,6:8])
y1.plot(MAallvax['Date'], MAvax['1stdose'], color = 'orange')
y1.plot(MAallvax['Date'], MAvax['Fullvax'], color = 'green')
# Set plot title and axes labels

#percentages text
MApop = 6893000
marks = [MApop*0.1, MApop*0.2, MApop*0.3, MApop*0.4, MApop*0.5, MApop*0.6, MApop*0.7]
marksv1 = []
marksv2 = []
c = 0
for x in MAvax.index:
    for y in range(len(marks)):
        if marks[c]<=MAvax.at[x,'1stdose'] and marks[c]>=MAvax.at[x-1,'1stdose'] :
            mark=x
            marksv1.append(mark)
            c=c+1
c=0
for x in MAvax.index:
    for y in range(len(marks)):
        if marks[c]<=MAvax.at[x,'Fullvax'] and marks[c]>=MAvax.at[x-1,'Fullvax'] :
            mark=x
            marksv2.append(mark)
            c=c+1
txt=['10%','20%','30%','40%','50%','60%','70%']
for i in range(len(marksv1)):
    plt.text(marksv1[i], marks[i], txt[i])
for i in range(len(marksv2)):
    plt.text(marksv2[i], marks[i], txt[i])




y1.set_xlabel('Date', loc='center', fontsize=18)
y1.set_ylabel('Vaccinated', loc='center', fontsize=18)
y1.xaxis.set_major_locator(ticker.MultipleLocator(14))
plt.setp(y1.get_xticklabels(), rotation = 90)

pop1 = (MAvax.loc[r-1, '1stdose']/MApop)*100
pop2 = (MAvax.loc[r-1, 'Fullvax']/MApop)*100
recent = '\n'.join(('1st dose: {:,.0f}'.format(MAvax.loc[r-1, '1stdose']),
                    'Full vax: {:,.0f}'.format(MAvax.loc[r-1, 'Fullvax']),
                    'Pop. 1st: %.2f'% pop1 + '%',
                    'Pop. full vax: %.2f'% pop2 + '%',
    MAallvax.loc[r-1, 'Date']))
y1.text(0.05, 0.95, recent, transform=y1.transAxes, fontsize=14,
        verticalalignment='top', bbox=props)
y1.yaxis.label.set_color('green')
plt.minorticks_on()
y1.tick_params(axis='x', direction='inout',which='minor', length=5, 
                bottom=True, top=False, left=False, right=False)
y1.tick_params(axis='x', direction='inout',which='major', length=10, 
                bottom=True, top=False, left=False, right=False,labelsize=14)
y1.tick_params(axis='y', colors='green', direction='out',which='minor', length=5, 
                bottom=False, top=False, left=True, right=False)
y1.tick_params(axis='y', colors='green', direction='out',which='major', length=10, 
                bottom=False, top=False, left=True, right=False, labelsize=14)
plt.grid(which='major', axis='both', alpha=0.1)

#sci notation
y1.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
#sci notation int location
y1.get_yaxis().get_offset_text().set_visible(False)
ax_max = max(y1.get_yticks())
exponent_axis = np.floor(np.log10(ax_max)).astype(int)
y1.annotate(r'$\times$10$^{%i}$'%(exponent_axis),  rotation = 90,
             xy=(0.01, .85), xycoords='axes fraction', fontsize=14, color='green')



MAflag = plt.imread(r'C:\Users\Bruno\Desktop\COVID19\Bandeira\Flag_Massachusetts.jpg')
newax = fig.add_axes([0.84, 0.87, 0.06, 0.06], zorder=1)
newax.imshow(MAflag, alpha=0.5)
newax.axis('off')



print('Mass data - complete.')



#_____________________________________________________________________________
# Curitiba
#_____________________________________________________________________________





print('Connection 3 OK. Saving data...')

nav = webdriver.Chrome()
nav.get('https://coronavirus.curitiba.pr.gov.br/#numerosCovid')
data_atual = nav.find_element_by_xpath('//*[@id="cphBodyMaster_lblDataAtualizacao"]')
total_obitos = nav.find_element_by_xpath('//*[@id="cphBodyMaster_lblObitos"]')
total_casos = nav.find_element_by_xpath('//*[@id="cphBodyMaster_lblConfirmados"]')

   
data_atual = data_atual.text


data_atual = data_atual.replace('Atualizado em ', '')
data_atual = data_atual[0:10]

total_obitos = total_obitos.text.replace('.','') 
total_obitos = int(total_obitos)
total_casos = total_casos.text.replace('.','') 
total_casos = int(total_casos)


nav.quit()

CWB = pd.read_csv (r"C:\Users\Bruno\Documents\GitHub\COVID_data_comp\Import Data\CWB_data2.csv", sep=",")


i = CWB['date'].iloc[-1]


if i != data_atual:
    ncases = total_casos - CWB['totalCases'].iloc[-1]
    ndeath = total_obitos - CWB['deaths'].iloc[-1]
    df2 = {'date': data_atual,'totalCases': total_casos, 'newCases':ncases ,'deaths': total_obitos, 'newDeaths':ndeath}
    CWB = CWB.append(df2, ignore_index=True)


r = len(CWB)
c = len(CWB.columns)

CWB.to_csv(r"C:\Users\Bruno\Documents\GitHub\COVID_data_comp\Import Data\CWB_data2.csv", index=False)

#Calculate 7 day means - Cases
CWBcases = CWB.loc[0:r, 'newCases']
CWBmeancase = list(range(r))
for x in range(len(CWBcases)):
    if x <= 6:
        CWBmeancase[x] = CWBcases[x]
    else:
        CWBmeancase[x] = statistics.mean(CWBcases[x-7:x])
CWB.insert(len(CWB.columns), "7dayMeanCases", CWBmeancase, True) 

#Calculate 7 day means - Death
CWBdeaths = CWB.loc[0:r, 'newDeaths']
CWBmeandeath = list(range(r))
for x in range(len(CWBdeaths)):
    if x <= 6:
        CWBmeandeath[x] = CWBdeaths[x]
    else:
        CWBmeandeath[x] = statistics.mean(CWBdeaths[x-7:x])
CWB.insert(len(CWB.columns), "7dayMeanDeaths", CWBmeandeath, True) 

#Last week diff.:
CWBmcasediff = ((CWB.loc[r-1, '7dayMeanCases'] - CWB.loc[r-8, '7dayMeanCases'])/CWB.loc[r-8, '7dayMeanCases'])*100
CWBmdeathdiff = ((CWB.loc[r-1, '7dayMeanDeaths'] - CWB.loc[r-8, '7dayMeanDeaths'])/CWB.loc[r-8, '7dayMeanDeaths'])*100

#__________________


# Define x and y axes - Suplot 1 cases
y1 = fig.add_subplot(gs[0,0:2])
y1.plot(CWB['date'], CWB['totalCases'], color = 'blue', linestyle='-', alpha=0.8)
# Set plot title and axes labels
y1.set_ylabel('Total Cases', loc='center',fontsize=18)
y1.xaxis.set_major_locator(ticker.MultipleLocator(30))
y1.set_title('Curitiba', fontsize=25, fontweight='bold')

recent = '\n'.join(('Total cases: {:,}'.format(CWB.loc[r-1, 'totalCases']),
    CWB.loc[r-1, 'date']))
y1.text(0.05, 0.95, recent, transform=y1.transAxes, fontsize=14,
        verticalalignment='top', bbox=props)

plt.minorticks_on()
y1.set_xticklabels([])
y1.yaxis.label.set_color('blue')
y1.tick_params(axis='x', direction='in',which='minor', length=5, 
                bottom=True, top=False, left=False, right=False)
y1.tick_params(axis='x', direction='in',which='major', length=10, 
                bottom=True, top=False, left=False, right=False)
y1.tick_params(axis='y', colors='blue', direction='out',which='minor', length=5, 
                bottom=False, top=False, left=True, right=False)
y1.tick_params(axis='y', colors='blue', direction='out',which='major', length=10, 
                bottom=False, top=False, left=True, right=False, labelsize=14)
plt.grid(which='major', axis='both', alpha=0.1)

#sci notation
y1.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
#sci notation int location
y1.get_yaxis().get_offset_text().set_visible(False)
ax_max = max(y1.get_yticks())
exponent_axis = np.floor(np.log10(ax_max)).astype(int)
y1.annotate(r'$\times$10$^{%i}$'%(exponent_axis),  rotation = 90,
             xy=(0.01, .85), xycoords='axes fraction', fontsize=14, color='blue')

plt.arrow(300, 1.3*ax_max/3, -100, 0, color='blue',head_width=ax_max/30, head_length=10)



# Define x and y axes - Suplot 1 death
y2 = y1.twinx()
y2.plot(CWB['date'], CWB['deaths'], color = 'red', linestyle='-.', alpha=0.8)
# Set plot title and axes labels

y2.xaxis.set_major_locator(ticker.MultipleLocator(30))
y2.set_ylabel('Total Deaths', loc='center',fontsize=18)
recent = '\n'.join(('Total deaths: {:,}'.format(CWB.loc[r-1, 'deaths']),
    CWB.loc[r-1, 'date']))
y2.text(0.95, 0.05, recent, transform=y1.transAxes, fontsize=14,
        verticalalignment='bottom',  horizontalalignment='right', bbox=props)


y2.yaxis.label.set_color('red')
y2.set_ylim([-0.2e3, 7e3])
plt.minorticks_on()
y2.tick_params(axis='y', colors='red', direction='out',which='minor', length=5, 
                bottom=False, top=False, left=False, right=True)
y2.tick_params(axis='y', colors='red', direction='out',which='major', length=10, 
                bottom=False, top=False, left=False, right=True, labelsize=14)

#sci notation
y2.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
#sci notation int location
y1.get_yaxis().get_offset_text().set_visible(False)
y2.get_yaxis().get_offset_text().set_visible(False)
ax_max = max(y2.get_yticks())
exponent_axis = np.floor(np.log10(ax_max)).astype(int)
y2.annotate(r'$\times$10$^{%i}$'%(exponent_axis), rotation = 90,
             xy=(0.975, .85), xycoords='axes fraction', fontsize=14, color='red')

plt.arrow(350, ax_max/3, 100, 0, color='red',head_width=ax_max/30, head_length=10)



#Bandeiras Curitiba
plt.text(93, 1.2*ax_max/4, 'Bandeira:')
#13/06/20 a 17/08: bandeira laranja
indice1 = CWB['date'].index[CWB['date'] =='13/06/2020']
indice2 = CWB['date'].index[CWB['date'] =='17/08/2020']
delta = int(indice2[0])-int(indice1[0])+1
plt.arrow(int(indice1[0]), ax_max/4, delta, 0, color='orange',linewidth=20,linestyle='-', alpha=0.2, head_length=0)
#18/08 a 6/09: bandeira amarela
indice1 = CWB['date'].index[CWB['date'] =='18/08/2020']
indice2 = CWB['date'].index[CWB['date'] =='06/09/2020']
delta = int(indice2[0])-int(indice1[0])+1
plt.arrow(int(indice1[0]), ax_max/4, delta, 0, color='yellow',linewidth=20,linestyle='-', alpha=0.2, head_length=0)
#7/09 a 27/09: bandeira laranja
indice1 = CWB['date'].index[CWB['date'] =='07/09/2020']
indice2 = CWB['date'].index[CWB['date'] =='27/09/2020']
delta = int(indice2[0])-int(indice1[0])+1
plt.arrow(int(indice1[0]), ax_max/4, delta, 0, color='orange',linewidth=20,linestyle='-', alpha=0.2, head_length=0)
#28/09 a 26/11: bandeira amarela
indice1 = CWB['date'].index[CWB['date'] =='28/09/2020']
indice2 = CWB['date'].index[CWB['date'] =='26/11/2020']
delta = int(indice2[0])-int(indice1[0])+1
plt.arrow(int(indice1[0]), ax_max/4, delta, 0, color='yellow',linewidth=20,linestyle='-', alpha=0.2, head_length=0)
#27/11 a 27/01: bandeira laranja
indice1 = CWB['date'].index[CWB['date'] =='27/11/2020']
indice2 = CWB['date'].index[CWB['date'] =='27/01/2021']
delta = int(indice2[0])-int(indice1[0])+1
plt.arrow(int(indice1[0]), ax_max/4, delta, 0, color='orange',linewidth=20,linestyle='-', alpha=0.2, head_length=0)
#28/01/21 a 24/02: bandeira amarela
indice1 = CWB['date'].index[CWB['date'] =='28/01/2021']
indice2 = CWB['date'].index[CWB['date'] =='24/02/2021']
delta = int(indice2[0])-int(indice1[0])+1
plt.arrow(int(indice1[0]), ax_max/4, delta, 0, color='yellow',linewidth=20,linestyle='-', alpha=0.2, head_length=0)
#25/02 a 12/03: bandeira laranja
indice1 = CWB['date'].index[CWB['date'] =='25/02/2021']
indice2 = CWB['date'].index[CWB['date'] =='12/03/2021']
delta = int(indice2[0])-int(indice1[0])+1
plt.arrow(int(indice1[0]), ax_max/4, delta, 0, color='orange',linewidth=20,linestyle='-', alpha=0.2, head_length=0)
#13/03 a 4/04: bandeira vermelha
indice1 = CWB['date'].index[CWB['date'] =='13/03/2021']
indice2 = CWB['date'].index[CWB['date'] =='04/04/2021']
delta = int(indice2[0])-int(indice1[0])+1
plt.arrow(int(indice1[0]), ax_max/4, delta, 0, color='red',linewidth=20,linestyle='-', alpha=0.2, head_length=0)
#5/04 a 27/05: bandeira laranja
indice1 = CWB['date'].index[CWB['date'] =='05/04/2021']
indice2 = CWB['date'].index[CWB['date'] =='27/05/2021']
delta = int(indice2[0])-int(indice1[0])+1
plt.arrow(int(indice1[0]), ax_max/4, delta, 0, color='orange',linewidth=20,linestyle='-', alpha=0.2, head_length=0)
#28/05 a 8/06: bandeira vermelha
indice1 = CWB['date'].index[CWB['date'] =='28/05/2021']
indice2 = CWB['date'].index[CWB['date'] =='08/06/2021']
delta = int(indice2[0])-int(indice1[0])+1
plt.arrow(int(indice1[0]), ax_max/4, delta, 0, color='red',linewidth=20,linestyle='-', alpha=0.2, head_length=0)
#9/06 a 7/07: bandeira laranja
indice1 = CWB['date'].index[CWB['date'] =='09/06/2021']
indice2 = CWB['date'].index[CWB['date'] =='07/07/2021']
delta = int(indice2[0])-int(indice1[0])+1
plt.arrow(int(indice1[0]), ax_max/4, delta, 0, color='orange',linewidth=20,linestyle='-', alpha=0.2, head_length=0)
#8/07 a atual: bandeira amarela
indice1 = CWB['date'].index[CWB['date'] =='08/07/2021']
indice2 = CWB['date'].index[CWB['date'] =='08/07/2021']
delta = int(indice2[0])-int(indice1[0])+1
plt.arrow(int(indice1[0]), ax_max/4, r-int(indice1[0]), 0, color='yellow',linewidth=20,linestyle='-', alpha=0.2, head_length=0)





# Define x and y axes - Suplot 2 new cases
y1 = fig.add_subplot(gs[1,0:2])
y1.bar(CWB['date'], CWB['newCases'], color = 'lightblue')
# Set plot title and axes labels
y1.set_ylabel('New Cases', loc='center',fontsize=18)
y1.xaxis.set_major_locator(ticker.MultipleLocator(30))

y1.plot(CWB['date'], CWB['7dayMeanCases'], color = 'magenta')
y1.set_ylim([0, 1600])

recent = '\n'.join((
    'New cases: {:,}'.format(CWB.loc[r-1, 'newCases']),
    'Last week diff.: %+.2f'% CWBmcasediff + '%',
    CWB.loc[r-1, 'date']))
y1.text(0.05, 0.95, recent, transform=y1.transAxes, fontsize=14,
        verticalalignment='top', bbox=props)

plt.minorticks_on()
y1.set_xticklabels([])
y1.yaxis.label.set_color('blue')
y1.tick_params(axis='x', direction='in',which='minor', length=5, 
                bottom=True, top=False, left=False, right=False)
y1.tick_params(axis='x', direction='in',which='major', length=10, 
                bottom=True, top=False, left=False, right=False)
y1.tick_params(axis='y', colors='blue', direction='out',which='minor', length=5, 
                bottom=False, top=False, left=True, right=False)
y1.tick_params(axis='y', colors='blue', direction='out',which='major', length=10, 
                bottom=False, top=False, left=True, right=False, labelsize=14)
plt.grid(which='major', axis='both', alpha=0.1)

#sci notation
y1.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
#sci notation int location
y1.get_yaxis().get_offset_text().set_visible(False)
ax_max = max(y1.get_yticks())
exponent_axis = np.floor(np.log10(ax_max)).astype(int)
y1.annotate(r'$\times$10$^{%i}$'%(exponent_axis),  rotation = 90,
             xy=(0.01, .85), xycoords='axes fraction', fontsize=14, color='blue')




# Define x and y axes - Suplot 3 new death
y1 = fig.add_subplot(gs[2,0:2])
y1.bar(CWB['date'], CWB['newDeaths'], color = 'pink')
# Set plot title and axes labels
y1.set_ylabel('New Deaths', loc='center',fontsize=18)
y1.xaxis.set_major_locator(ticker.MultipleLocator(30))
plt.setp(y1.get_xticklabels(), rotation = 90)

y1.plot(CWB['date'], CWB['7dayMeanDeaths'], color = 'magenta')
y1.set_ylim([0, 50])

recent = '\n'.join((
    'New deaths: {:,}'.format(CWB.loc[r-1, 'newDeaths']),
    'Last week diff.: %+.2f'% CWBmdeathdiff + '%',
    CWB.loc[r-1, 'date']))
y1.text(0.05, 0.95, recent, transform=y1.transAxes, fontsize=14,
        verticalalignment='top', bbox=props)
y1.yaxis.label.set_color('red')

plt.minorticks_on()
y1.tick_params(axis='x', direction='inout',which='minor', length=5, 
                bottom=True, top=False, left=False, right=False)
y1.tick_params(axis='x', direction='inout',which='major', length=10, 
                bottom=True, top=False, left=False, right=False,labelsize=14)
y1.tick_params(axis='y', colors='red', direction='out',which='minor', length=5, 
                bottom=False, top=False, left=True, right=False)
y1.tick_params(axis='y', colors='red', direction='out',which='major', length=10, 
                bottom=False, top=False, left=True, right=False, labelsize=14)
plt.grid(which='major', axis='both', alpha=0.1)

#sci notation
y1.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
#sci notation int location
y1.get_yaxis().get_offset_text().set_visible(False)
ax_max = max(y1.get_yticks())
exponent_axis = np.floor(np.log10(ax_max)).astype(int)
y1.annotate(r'$\times$10$^{%i}$'%(exponent_axis),  rotation = 90,
             xy=(0.01, .85), xycoords='axes fraction', fontsize=14, color='red')


#_____________________________

#CWB vaccine


nav = webdriver.Chrome()
nav.get('https://coronavirus.curitiba.pr.gov.br/#numerosCovid')
data_atualvax = nav.find_element_by_xpath('//*[@id="cphBodyMaster_ucVacinometro_lblDataAtualizacaoVacinacao"]')
dose1 = nav.find_element_by_xpath('//*[@id="cphBodyMaster_ucVacinometro_lblContadorVacinas"]')
dose2 = nav.find_element_by_xpath('//*[@id="cphBodyMaster_ucVacinometro_lblContadorSegundaDose"]')

    
data_atualvax = data_atualvax.text
dose1 = int(dose1.text)
dose2 = int(dose2.text)

nav.quit()


df = pd.read_csv (r'C:\Users\Bruno\Documents\GitHub\COVID_data_comp\Import Data\CWBvax.csv')

i = df['Data'].iloc[-1]


if i != data_atualvax:
    df2 = {'Data': data_atualvax,'Total1dose': dose1, 'Total2dose': dose2}
    df = df.append(df2, ignore_index=True)

df.to_csv(r'C:\Users\Bruno\Documents\GitHub\COVID_data_comp\Import Data\CWBvax.csv', index=False)

r = len(df)
c = len(df.columns)


# Define x and y axes - Suplot 4vax
y1 = fig.add_subplot(gs[4,0:2])
y1.plot(df['Data'], df['Total1dose'], color = 'orange')
y1.plot(df['Data'], df['Total2dose'], color = 'green')
# Set plot title and axes labels

#percentages text
CWBpop = 1948626
marks = [CWBpop*0.1, CWBpop*0.2, CWBpop*0.3, CWBpop*0.4, CWBpop*0.5, CWBpop*0.6, CWBpop*0.7]
marksv1 = []
marksv2 = []
c = 0
for x in df.index:
    for y in range(len(marks)):
        if marks[c]<=df.at[x,'Total1dose'] and marks[c]>=df.at[x-1,'Total1dose'] :
            mark=x
            marksv1.append(mark)
            c=c+1
c=0
for x in df.index:
    for y in range(len(marks)):
        if marks[c]<=df.at[x,'Total2dose'] and marks[c]>=df.at[x-1,'Total2dose'] :
            mark=x
            marksv2.append(mark)
            c=c+1
txt=['10%','20%','30%','40%','50%','60%','70%']
for i in range(len(marksv1)):
    plt.text(marksv1[i], marks[i], txt[i])
for i in range(len(marksv2)):
    plt.text(marksv2[i], marks[i], txt[i])


y1.set_xlabel('Date', loc='center', fontsize=18)
y1.set_ylabel('Vaccinated', loc='center', fontsize=18)
y1.xaxis.set_major_locator(ticker.MultipleLocator(14))
plt.setp(y1.get_xticklabels(), rotation = 90)

pop1 = (df.loc[r-1, 'Total1dose']/CWBpop)*100
pop2 = (df.loc[r-1, 'Total2dose']/CWBpop)*100
recent = '\n'.join(('1st dose: {:,.0f}'.format(df.loc[r-1, 'Total1dose']),
                    'Ful vax: {:,.0f}'.format(df.loc[r-1, 'Total2dose']),
                    'Pop. 1st: %.2f'% pop1 + '%',
                    'Pop. full vax: %.2f'% pop2 + '%',
    df.loc[r-1, 'Data']))
y1.text(0.05, 0.95, recent, transform=y1.transAxes, fontsize=14,
        verticalalignment='top', bbox=props)
y1.yaxis.label.set_color('green')
plt.minorticks_on()
y1.tick_params(axis='x', direction='inout',which='minor', length=5, 
                bottom=True, top=False, left=False, right=False)
y1.tick_params(axis='x', direction='inout',which='major', length=10, 
                bottom=True, top=False, left=False, right=False,labelsize=14)
y1.tick_params(axis='y', colors='green', direction='out',which='minor', length=5, 
                bottom=False, top=False, left=True, right=False)
y1.tick_params(axis='y', colors='green', direction='out',which='major', length=10, 
                bottom=False, top=False, left=True, right=False, labelsize=14)
plt.grid(which='major', axis='both', alpha=0.1)

#sci notation
y1.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
#sci notation int location
y1.get_yaxis().get_offset_text().set_visible(False)
ax_max = max(y1.get_yticks())
exponent_axis = np.floor(np.log10(ax_max)).astype(int)
y1.annotate(r'$\times$10$^{%i}$'%(exponent_axis),  rotation = 90,
             xy=(0.01, .85), xycoords='axes fraction', fontsize=14, color='green')




CWBflag = plt.imread(r'C:\Users\Bruno\Desktop\COVID19\Bandeira\Flag_Curitiba.png')
newax = fig.add_axes([0.1, 0.86, 0.06, 0.06], zorder=1)
newax.imshow(CWBflag, alpha=0.5)
newax.axis('off')



print('Curitiba data - complete.')



#_____________________________________________________________________________

print('Plotting...')

# Save Figure
#fig.tight_layout()
fig.subplots_adjust(left=0.03, right=0.97, top=0.93, bottom=0.08)

plt.show()

folder = r'C:\Users\Bruno\Documents\GitHub\COVID_data_comp\Graphs\\'
fig.savefig(folder + today + ".png")

# Update README file
f = open(r"C:\Users\Bruno\Documents\GitHub\COVID_data_comp\README.md", "w")
descrip = '''
# COVID_data_comp
COVID data compilation from CWB, PR, BR and MA.

<img src="Graphs/{}.png" >


## Sources:
- Curitiba:
    - Prefeitura Municipal de Curitiba <https://coronavirus.curitiba.pr.gov.br/painelcovid/>

- Paraná:
    - Wesley Cota, PhD (Universidade Federal de Viçosa) <https://covid19br.wcota.me/>

- Brazil:
    - Wesley Cota, PhD (Universidade Federal de Viçosa) <https://covid19br.wcota.me/>

- Massachusetts:
    - New York times <https://github.com/nytimes/covid-19-data>
    - Johns Hopkins Centers for Civic Impact for the Coronavirus Resource Center <https://github.com/govex/COVID-19>
    
'''.format(today)
f.write(descrip)
f.close()


print('Save complete. Updating Git...')


# Git commands to track version and upload to Github
from git import Repo

repo = Repo(r'C:\Users\Bruno\Documents\GitHub\COVID_data_comp\.git')
repo.git.add('--all')  # to add all the working files.
repo.git.commit('-m', 'Daily update') #Commit and comment
origin = repo.remote(name='origin')
origin.push() #push to Github


print('Github upload complete.')

#_____________________________________________________________________________

