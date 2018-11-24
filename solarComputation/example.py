import solarPanelClass as sp

sp = sp.solarPanel('1652 Culpepper Dr, Petaluma, CA 94954, USA',16)

print("meanLightIntensity = "+str(sp.meanLightIntensity)+"W/m^2 (mean over 24h)")
print("investmentPrice    = "+str(sp.investmentPrice)+"$")
print("elecPower          = "+str(sp.elecPower)+"W (mean over 24h)")
print("monthlySaving      = "+str(sp.monthlySaving)+"$")