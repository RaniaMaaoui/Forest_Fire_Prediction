import math

class FWI:
    def FFMC(self, TEMP, RH, WIND, RAIN, FFMCPrev):
        RH = min(100.0, RH)
        mo = 147.2 * (101.0 - FFMCPrev) / (59.5 + FFMCPrev)

        if RAIN > .5:
            rf = RAIN - .5
            if mo <= 150.0:
                mr = mo + 42.5 * rf * math.exp(-100.0 / (251.0 - mo)) * (1.0 - math.exp(-6.93 / rf))
            else:
                mr = mo + 42.5 * rf * math.exp(-100.0 / (251.0 - mo)) * (1.0 - math.exp(-6.93 / rf)) + 0.0015 * pow(mo - 150.0, 2) * pow(rf, .5)
            if mr > 250.0:
                mr = 250.0
            mo = mr

        ed = 0.942 * pow(RH, 0.679) + 11.0 * math.exp((RH - 100.0) / 10.0) + 0.18 * (21.1 - TEMP) * (1.0 - math.exp(-0.115 * RH))

        if mo > ed:
            ko = 0.424 * (1.0 - pow(RH / 100.0, 1.7)) + 0.0694 * pow(WIND, .5) * (1.0 - pow(RH / 100.0, 8))
            kd = ko * 0.581 * math.exp(0.0365 * TEMP)
            m = ed + (mo - ed) * pow(10.0, -kd)
        else:
            ew = 0.618 * pow(RH, 0.753) + 10.0 * math.exp((RH - 100.0) / 10.0) + 0.18 * (21.1 - TEMP) * (1.0 - math.exp(-0.115 * RH))
            if mo < ew:
                k1 = 0.424 * (1.0 - pow((100.0 - RH) / 100.0, 1.7)) + 0.0694 * pow(WIND, .5) * (1.0 - pow((100.0 - RH) / 100.0, 8))
                kw = k1 * 0.581 * math.exp(0.0365 * TEMP)
                m = ew - (ew - mo) * pow(10.0, -kw)
            else:
                m = mo

        return 59.5 * (250.0 - m) / (147.2 + m)

    def ISI(self, WIND, FFMC):
        fWIND = math.exp(0.05039 * WIND)
        m = 147.2 * (101.0 - FFMC) / (59.5 + FFMC)
        fF = 91.9 * math.exp(-0.1386 * m) * (1.0 + pow(m, 5.31) / 49300000.0)
        return 0.208 * fWIND * fF


    def FWI(self, ISI):
        return ISI * 0.1  


    def calculate_wind(self, temp, humidity, pressure):
        wind_temp_factor = 0.1
        wind_humidity_factor = 0.07
        wind_pressure_factor = 0.05

        wind_from_temp = temp * wind_temp_factor
        wind_from_humidity = humidity * wind_humidity_factor
        wind_from_pressure = (1013 - pressure) * wind_pressure_factor

        estimated_wind_speed = wind_from_temp + wind_from_humidity + wind_from_pressure
        return round(max(0, estimated_wind_speed), 2)
