#include <stdio.h>
#include <math.h>

#include <pybind11/pybind11.h>
namespace py = pybind11;


double ciede2000(double L1, double a1, double b1, 
                 double L2, double a2, double b2) {
	
	// 1. Calculate Ci', hi':
	double C1 = sqrt(a1*a1 + b1*b1);
	double C2 = sqrt(a2*a2 + b2*b2);
	double C = (C1 + C2) / 2.0;

	double G = 0.5 * (1 - sqrt(pow(C, 7.0) / (pow(C, 7.0)+pow(25, 7.0))));
	
	double aPrime1 = (1 + G) * a1;
	double aPrime2 = (1 + G) * a2;
	double CPrime1 = sqrt(aPrime1*aPrime1 + b1*b1);
	double CPrime2 = sqrt(aPrime2*aPrime2 + b2*b2);
	double hPrime1 = (b1 == aPrime1 and b1 == 0)? 0:atan2(b1, aPrime1);
	double hPrime2 = (b2 == aPrime2 and b2 == 0)? 0:atan2(b2, aPrime2);

	// 2. Calculate delta L', delta C' delta H':
	double dLPrime = L2 - L1;
	double dCPrime = CPrime2 - CPrime1;

	double dh = hPrime2 - hPrime1;
	double dhPrime = 0;
	double CC = CPrime1 * CPrime2;

	if (CC != 0) {
		if (abs(dh) <= M_PI) 
			dhPrime = dh;
		else if (dh > M_PI)
			dhPrime = dh - 2*M_PI;
		else if (dh < -M_PI)
			dhPrime = dh + 2*M_PI;
	}

	double dHPrime = 2 * sqrt(CC) * sin(dhPrime/2.0);

	// 3. Calculate CIEDE2000 Color-Difference delta E00:
	double LBPrime = (L1 + L2) / 2.0;
	double CBPrime = (CPrime1 + CPrime2) / 2.0;
	double hBPrime = (hPrime1 + hPrime2);

	if (CC != 0) {
		if (abs(dh) <= M_PI)
			hBPrime /= 2.0;
		else if (abs(dh) > M_PI and hBPrime < 2*M_PI)
			hBPrime = (hBPrime + 2*M_PI) / 2.0;
		else if (abs(dh) > M_PI and hBPrime >= 2*M_PI)
			hBPrime = (hBPrime - 2*M_PI) / 2.0;
	}

	double T = 1 - 0.17*cos(hBPrime - M_PI/6.0) // 30 degree
				 + 0.24*cos(2*hBPrime)
				 + 0.32*cos(3*hBPrime + M_PI/30.0) // 6 degree
				 - 0.20*cos(4*hBPrime - M_PI*(7.0/20.0)); // 63 degree

	double dTheta = M_PI/6.0 * // 30 degree
					exp(-pow((hBPrime - M_PI*(55.0/36.0))/(M_PI*(5.0/36.0)), 2.0)); // 275, 25 degree

	double Rc = 2 * sqrt(pow(CBPrime, 7) / (pow(CBPrime, 7) + pow(25, 7)));
	double Sl = 1 + (0.015 * pow(LBPrime-50, 2)) / sqrt(20 + pow(LBPrime-50, 2));
	double Sc = 1 + 0.045 * CBPrime;
	double Sh = 1 + 0.015 * CBPrime * T;
	double Rt = -sin(2 * dTheta) * Rc;
	const double kl = 1.0, kc = 1.0, kh = 1.0;

	double dE00 = sqrt(pow(dLPrime/(kl*Sl), 2)
	                  +pow(dCPrime/(kc*Sc), 2)
	                  +pow(dHPrime/(kh*Sh), 2)
	                  +Rt*(dCPrime/(kc*Sc))*(dHPrime/(kh*Sh)));

	return dE00;
}

PYBIND11_MODULE(ciede2000, m) {
	m.doc() = "pybind ciede2000 plugin";
	m.def("ciede2000", &ciede2000, 
	      "A function which calculate perception distance between two colors.");
}