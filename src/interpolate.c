
#include "simulator.h"

// Make a table for interpolating func(x) by doing
//
//   k = (int)(x-start)/scale;
//   y = (a[k] * x + b[k]) * x  + c[k];
//   y' = 2 * a[k] * x + b[k];
//
static void
fillInterpolationTable(struct interpolationTable *t,
                       double func(double, void *),
                       double dfunc(double, void *),
                       double start,
                       double scale,
                       void *parameters)
{
  // code to shift points to minimize distance to actual function is
  // in version 1.26 and earlier.
  int k;
  double x1;  // x position of left edge of interpolation interval
  double y1;  // func(x1)
  double y1p; // dfunc(x1)   derivitive of func at x1
  double x2;  // x position of right edge of interpolation interval
  double y2;  // func(x2)
  double y2p; // dfunc(x2)   derivitive of func at x2

  t->start = start;
  t->scale = scale;
    
  x2 = start;
  y2 = func(x2, parameters);
  y2p = dfunc(x2, parameters) / 1000000.0;
	
  for (k=0; k<TABLEN; k++) {
    x1 = x2;
    y1 = y2;
    y1p = y2p;

    x2 = start + (double)((k + 1) * scale);
    y2 = func(x2, parameters);
    y2p = dfunc(x2, parameters) / 1000000.0;

    // y = Ax^2 + Bx + C
    // y' = 2Ax + B
    //
    // y1p = 2 A x1 + B
    // y2p = 2 A x2 + B
    // y1p - y2p = 2 A (x1 - x2)
    t->a[k] = (y1p - y2p) / (2.0 * (x1 - x2));

    // B = y2p - 2 A x2
    t->b[k] = y2p - 2.0 * t->a[k] * x2; // note, x2 should always be > 0

    // C = y2 - (A x2 + B) x2
    t->c[k] = y2 - (t->a[k] * x2 + t->b[k]) * x2;
    //fprintf(stderr, "%d %e %e %e ... %e %e %e\n", k, t->a[k], t->b[k], t->c[k], x2, y2, y2p);
  }
}

/** stiffnesses are in N/m, so forces come out in pN (i.e. Dx N) */

static double
lippincott(double r, struct bondStretch *s)
{
  return s->de * (1 - exp(-1e-6 * s->ks * s->r0 * (r - s->r0) * (r - s->r0) / (2 * s->de * r)));
}

static double
morse(double r, struct bondStretch *s)
{
  // the exponent is unitless
  // returns potential in aJ, given r in pm
  return s->de * (1 - exp(-s->beta * (r - s->r0))) * (1 - exp(-s->beta * (r - s->r0)));
}


// use the Morse potential inside R0, Lippincott outside
// result in aJ
double
potentialLippincottMorse(double r, void *p)
{
  struct bondStretch *stretch = (struct bondStretch *)p;
  return (r >= stretch->r0) ? lippincott(r, stretch) : morse(r, stretch);
}

// numerically differentiate the potential for force
//
// the result is in yoctoJoules per picometer = picoNewtons
// yJ / pm = 1e-24 J / 1e-12 m = 1e-12 J / m = pN
#define DELTA_R 0.01
double
gradientLippincottMorse(double r, void *p)
{
  struct bondStretch *stretch = (struct bondStretch *)p;
  double r1 = r - DELTA_R / 2.0;
  double r2 = r + DELTA_R / 2.0;
  double y1 = (r1 >= stretch->r0) ? lippincott(r1, stretch) : morse(r1, stretch);
  double y2 = (r2 >= stretch->r0) ? lippincott(r2, stretch) : morse(r2, stretch);
  // y1, y2 are in attoJoules (1e-18 J)
  // DELTA_R is in pm (1e-12 m), so:
  // (y2-y1)/DELTA_R is attoJoules / pm (1e-6 J / m)
  // 1e6*(y2-y1) is in 1e-12 J/m, or pN

  return 1e6 * (y2 - y1) / DELTA_R;
}

static void
findPotentialExtension(struct bondStretch *s, double r0, double pr0, double gr0, double r1, double pr1, double gr1)
{
  double r02 = r0 * r0;
  double r03 = r02 * r0;
  double r12 = r1 * r1;
  double r13 = r12 * r1;
  double r14 = r12 * r12;
  double d2r1 = 0.01;
  double denom;

  gr1 /= DR;
  
  // we are solving the following simultaneous equations:
  //
  // A + B r0 + C r0^2 + D r0^3 == pr0
  // A + B r1 + C r1^2 + D r1^3 == pr1
  // B + 2 C r1 + 3 D r1^2 == gr1
  // 2 C + 6 D r1 == d2r1
  //
  // The first two lines give the cubic extension for the potential
  // function.  We want it to match the actual potential function at
  // r0 (the minimum, should be zero), and r1 (the point where we cut
  // over from the interpolation table to the polynomial functions).
  //
  // The third line gives the derivative, which we want to match the
  // actual gradient function at r1.
  //
  // The last line gives the second derivative, which we want to be
  // positive so the curve keeps going up.  We just pick an arbitrary
  // constant here.
  //
  // The expressions below are generated by Mathematica, handing the
  // above equations to "Solve[.....] // InputForm", then removing the
  // ^ characters, so r1^3 becomes r13, which we have pre-computed.
  //
  // XXX might want to try specifying the third derivative instead of
  // the curve match at r0.
  
  denom = 2*(r0 - r1)*(r0 - r1)*(r0 - r1);

  s->potentialExtensionA = 
    -(-2*pr1*r03 + 6*pr1*r02*r1 + 
      2*gr1*r03*r1 - 6*pr1*r0*r12 - 
      6*gr1*r02*r12 - d2r1*r03*r12 + 
      2*pr0*r13 + 4*gr1*r0*r13 + 
      2*d2r1*r02*r13 - d2r1*r0*r14)
    /denom;
  
  s->potentialExtensionB =
    -(-2*gr1*r03 + 6*gr1*r02*r1 + 
      2*d2r1*r03*r1 - 6*pr0*r12 + 
      6*pr1*r12 - 3*d2r1*r02*r12 - 
      4*gr1*r13 + d2r1*r14)
    /denom;
  s->potentialExtensionC =
    -(-(d2r1*r03) + 6*pr0*r1 - 
      6*pr1*r1 - 6*gr1*r0*r1 + 6*gr1*r12 + 
      3*d2r1*r0*r12 - 2*d2r1*r13)
    /denom;
  
  s->potentialExtensionD =
    -(-2*pr0 + 2*pr1 + 2*gr1*r0 + 
      d2r1*r02 - 2*gr1*r1 - 2*d2r1*r0*r1 + 
      d2r1*r12)
    /denom;
}

// Examine a potential interpolation table to find where it exceeds a
// global maximum physical energy.  Those index values are recorded,
// so we can test for them during a dynamics run and issue a warning.
// The idea is that too much energy in a single bond might indicate
// that the simulation is suspect (would require a quantum
// calculation).
static int
findExcessiveEnergyLevel(struct interpolationTable *t,
                         double r0,
                         int searchIncrement,
                         int searchLimit,
                         double minPotential,
                         char *name)
{
  double start = t->start;
  double scale = t->scale;
  double *a = t->a;
  double *b = t->b;
  double *c = t->c;
  int k;
  double x;
  double potential = 0.0;
  
  k = (int)(r0 - start) / scale;
  while ((searchLimit-k)*searchIncrement > 0) {
    x = k * scale + start;
    potential = (a[k] * x + b[k]) * x + c[k] - minPotential;
    if (potential > ExcessiveEnergyLevel) {
      return k;
    }
    k += searchIncrement;
  }
  WARNING3("ExcessiveEnergyLevel %e exceeds interpolation table limits at %e for %s",
           ExcessiveEnergyLevel, potential, name);
  return searchLimit;
}

#if 0
static double
potentialQuadratic(double r, void *p)
{
  struct bondStretch *stretch = (struct bondStretch *)p;
  double dr = r - stretch->r0;
  return stretch->ks * dr * dr;
}

static double
gradientQuadratic(double r, void *p)
{
  double r1 = r - DELTA_R / 2.0;
  double r2 = r + DELTA_R / 2.0;
  double y1 = potentialQuadratic(r1, p);
  double y2 = potentialQuadratic(r2, p);
  // y1, y2 are in attoJoules (1e-18 J)
  // DELTA_R is in pm (1e-12 m), so:
  // (y2-y1)/DELTA_R is attoJoules / pm (1e-6 J / m)
  // 1e6*(y2-y1) is in 1e-12 J/m, or pN

  return 1e6 * (y2 - y1) / DELTA_R;
}
#endif

// Initialize the function interpolation tables for each stretch
void
initializeBondStretchInterpolater(struct bondStretch *stretch)
{
  double scale;
  double rmin;
  double rmax;

  rmin = stretch->r0 * 0.5;
  rmax = stretch->inflectionR;

  scale = (rmax - rmin) / TABLEN;

  findPotentialExtension(stretch,
                         stretch->r0,
                         potentialLippincottMorse(stretch->r0, stretch),
                         gradientLippincottMorse(stretch->r0, stretch),
                         rmax,
                         potentialLippincottMorse(rmax, stretch),
                         gradientLippincottMorse(rmax, stretch)
                         );
  fillInterpolationTable(&stretch->LippincottMorse,
                         potentialLippincottMorse,
                         gradientLippincottMorse,
                         rmin, scale, stretch);
  stretch->maxPhysicalTableIndex = findExcessiveEnergyLevel(&stretch->LippincottMorse,
                                                            stretch->r0, 1, TABLEN, 0.0, stretch->bondName);
  stretch->minPhysicalTableIndex = findExcessiveEnergyLevel(&stretch->LippincottMorse,
                                                            stretch->r0, -1, 0, 0.0, stretch->bondName);
  
}


/* the Buckingham potential for van der Waals / London force */
// result in aJ
double
potentialBuckingham(double r, void *p)
{
  struct vanDerWaalsParameters *vdw = (struct vanDerWaalsParameters *)p;
	
  // rvdW in pm (1e-12 m)
  // evdW in zJ (1e-21 J)
  return 1e-3 * vdw->evdW * (2.48e5 * exp(-12.5*(r/vdw->rvdW)) -1.924*pow(r/vdw->rvdW, -6.0))
    - vdw->vInfinity;
}

// the result is in yoctoJoules per picometer = picoNewtons
// yJ / pm = 1e-24 J / 1e-12 m = 1e-12 J / m = pN
//
// NOTE: gradient is divided by r since we end up multiplying it by
// the radius vector to get the force.
double
gradientBuckingham(double r, void *p)
{
  struct vanDerWaalsParameters *vdw = (struct vanDerWaalsParameters *)p;
  double y;

  // rvdW in pm (1e-12 m)
  // evdW in zJ (1e-21 J)
  y= -1e3 * vdw->evdW * (2.48e5 * exp(-12.5 * (r / vdw->rvdW)) * (-12.5 /vdw->rvdW)
                         - 1.924 * pow (1.0 /vdw->rvdW, -6.0) * (-6.0) * pow(r, -7.0));
  return y / r;
}

void
initializeVanDerWaalsInterpolator(struct vanDerWaalsParameters *vdw, int element1, int element2)
{
  double start;
  double scale;
  double end;

  // periodicTable[].vanDerWaalsRadius is in 1e-10 m
  // so rvdW is in 1e-12 m or pm
  vdw->rvdW = 100.0 * (periodicTable[element1].vanDerWaalsRadius +
                  periodicTable[element2].vanDerWaalsRadius);
  // evdW in 1e-21 J or zJ
  vdw->evdW = (periodicTable[element1].e_vanDerWaals + periodicTable[element2].e_vanDerWaals) / 2.0;

  start = vdw->rvdW * 0.4;
  end = vdw->rvdW * 1.5;
  scale = (end - start) / TABLEN;

  vdw->vInfinity = 0.0;
  vdw->vInfinity = potentialBuckingham(end, vdw);
  
  fillInterpolationTable(&vdw->Buckingham,
                         potentialBuckingham,
                         gradientBuckingham,
                         start, scale, vdw);
  vdw->minPhysicalTableIndex = findExcessiveEnergyLevel(&vdw->Buckingham,
                                                        vdw->rvdW, -1, 0,
                                                        potentialBuckingham(vdw->rvdW, vdw),
                                                        vdw->vdwName);
}

static void
convertDashToSpace(char *s)
{
  while (*s) {
    if (*s == '-') {
      *s = ' ';
    }
    s++;
  }
}

static void
printBondPAndG(char *bondName, double initial, double increment, double limit)
{
  char elt1[4];
  char elt2[4];
  char order;
  struct atomType *e1;
  struct atomType *e2;
  struct bondStretch *stretch;
  double r;
  double interpolated_potential;
  double interpolated_gradient;
  double direct_potential;
  double direct_gradient;
  double extension_potential;
  double extension_gradient;
  double lip; // last interpolated_potential
  double dip; // derivitive of interpolated_potential
  
  convertDashToSpace(bondName);
  if (3 != sscanf(bondName, "%2s %c %2s", elt1, &order, elt2)) {
    fprintf(stderr, "bond format must be: bond:C-1-H\n");
    exit(1);
  }
  e1 = getAtomTypeByName(elt1);
  if (e1 == NULL) {
    fprintf(stderr, "Element %s not defined\n", elt1);
    exit(1);
  }
  e2 = getAtomTypeByName(elt2);
  if (e2 == NULL) {
    fprintf(stderr, "Element %s not defined\n", elt2);
    exit(1);
  }
  
  // XXX this may return completly bizarre result for unknown bond orders.
  stretch = getBondStretch(e1->protons, e2->protons, order);

  printf("# ks=%e r0=%e de=%e beta=%e inflectionR=%e\n",
         stretch->ks,
         stretch->r0,
         stretch->de,
         stretch->beta,
         stretch->inflectionR);

  printf("# table start = %e table end = %e\n",
         stretch->r0 * 0.5,
         stretch->inflectionR);

  interpolated_potential = stretchPotential(NULL, NULL, stretch, initial);
  for (r=initial; r<limit; r+=increment) {
    lip = interpolated_potential;
    interpolated_potential = stretchPotential(NULL, NULL, stretch, r);
    dip = interpolated_potential - lip;
    interpolated_gradient = stretchGradient(NULL, NULL, stretch, r);
    direct_potential = potentialLippincottMorse(r, stretch);
    direct_gradient = gradientLippincottMorse(r, stretch);
    extension_potential =
      + stretch->potentialExtensionA
      + stretch->potentialExtensionB * r
      + stretch->potentialExtensionC * r * r
      + stretch->potentialExtensionD * r * r * r;
    extension_gradient =
      + stretch->potentialExtensionB
      + stretch->potentialExtensionC * r * 2.0
      + stretch->potentialExtensionD * r * r * 3.0;
    extension_gradient *= DR;
    printf("%13.6e %13.6e %13.6e %13.6e %13.6e %13.6e %13.6e %13.6e\n",
           r,                      // 1
           interpolated_potential, // 2
           interpolated_gradient, // 3
           direct_potential,       // 4
           direct_gradient,       // 5
           extension_potential,    // 6
           extension_gradient,    // 7
           dip                    // 8
           );
  }
}

static void
printBendPAndG(char *bendName, double initial, double increment, double limit)
{
  fprintf(stderr, "printBendPAndG not implemented yet\n");
  exit(1);
}

static void
printVdWPAndG(char *vdwName, double initial, double increment, double limit)
{
  char elt1[4];
  char elt2[4];
  struct atomType *e1;
  struct atomType *e2;
  struct vanDerWaalsParameters *vdw;
  double r;
  double interpolated_potential;
  double interpolated_gradient;
  double direct_potential;
  double direct_gradient;
  double lip; // last interpolated_potential
  double dip; // derivitive of interpolated_potential
  
  convertDashToSpace(vdwName);
  if (2 != sscanf(vdwName, "%2s v %2s", elt1, elt2)) {
    fprintf(stderr, "vdw format must be: vdw:C-v-H\n");
    exit(1);
  }
  e1 = getAtomTypeByName(elt1);
  if (e1 == NULL) {
    fprintf(stderr, "Element %s not defined\n", elt1);
    exit(1);
  }
  e2 = getAtomTypeByName(elt2);
  if (e2 == NULL) {
    fprintf(stderr, "Element %s not defined\n", elt2);
    exit(1);
  }
  
  vdw = getVanDerWaalsTable(e1->protons, e2->protons);

  printf("# rvdW=%e evdW=%e\n",
         vdw->rvdW,
         vdw->evdW);

  printf("# table start = %e table end = %e\n",
         vdw->rvdW * 0.4,
         vdw->rvdW * 1.5);

  interpolated_potential = vanDerWaalsPotential(NULL, NULL, vdw, initial);
  for (r=initial; r<limit; r+=increment) {
    lip = interpolated_potential;
    interpolated_potential = vanDerWaalsPotential(NULL, NULL, vdw, r);
    dip = interpolated_potential - lip;
    interpolated_gradient = vanDerWaalsGradient(NULL, NULL, vdw, r);
    direct_potential = potentialBuckingham(r, vdw);
    direct_gradient = gradientBuckingham(r, vdw);
    printf("%13.6e %13.6e %13.6e %13.6e %13.6e %13.6e\n",
           r,                      // 1
           interpolated_potential, // 2
           interpolated_gradient, // 3
           direct_potential,       // 4
           direct_gradient,       // 5
           dip                    // 6
           );
  }
}

void
printPotentialAndGradientFunctions(char *name, double initial, double increment, double limit)
{

  if (!strncmp(name, "bond:", 5)) {
    printBondPAndG(name+5, initial, increment, limit);
  } else if (!strncmp(name, "bend:", 5)) {
    printBendPAndG(name+5, initial, increment, limit);
  } else if (!strncmp(name, "vdw:", 4)) {
    printVdWPAndG(name+4, initial, increment, limit);
  } else {
    fprintf(stderr, "You must specify the type of entry you want printed.\n");
    fprintf(stderr, "For example:\n");
    fprintf(stderr, " bond:C-1-H\n");
    fprintf(stderr, " bend:C-1-C-1-H\n");
    fprintf(stderr, " vdw:C-v-H\n");
    exit(1);
  }
}

// ks in N/m
// r0 in pm, or 1e-12 m
// de in aJ, or 1e-18 J
// beta in 1e10 m^-1
//                                        ks     r0      de     beta   inflectionR
//  addInitialBondStretch(  6,  6, '1',  437.8, 154.9, 0.7578, 1.6996, 196.3800); // C-C

// kb in aJ / rad^2
// theta0 in radians
//                                  kb             theta0
//  addInitialBendData("C-1-C-1-C", 1.09340661193, 1.93035002646);

#define POLAR
#ifdef POLAR
// a->r
// b->theta
#define A_MIN 140
#define A_MAX 220
#define A_INCR 5
#define B_MIN (0)
#define B_MAX (2*Pi)
#define B_INCR 0.2
#define X(a, b) ((a) * sin(b))
#define Y(a, b) ((a) * cos(b))
#else
// a->x
// b->y
#define A_MIN -500
#define A_MAX 500
#define A_INCR 25
#define B_MIN -500
#define B_MAX 500
#define B_INCR 25
#define X(a, b) (a)
#define Y(a, b) (b)
#endif
#define ZOFFSET -50.0
#define ZTICK -2.0
#define POTENTIAL_SCALE 500
#define FORCE_SCALE 0.002

#define POTENTIAL_CUTOFF (0.5 * POTENTIAL_SCALE)
#define FORCE_CUTOFF (100 / FORCE_SCALE)

// run with -D 8
void
printBendStretch()
{
  struct part *p;
  struct xyz pos[3];
  struct xyz force[3];
  FILE *out;
  double a;
  double b;
  double x;
  double y;
  double x1;
  double y1;
  double x2;
  double y2;
  double potential;
  double prevA_potential;
  double prevB_potential = 0.0;
  double flen;
  float red, grn, blu;
  int red1, red2;

  out = fopen("forceresult", "w");
  p = makePart("internal", NULL, NULL);
  pos[0].x = 0;
  pos[0].y = 0;
  pos[0].z = 0;
  makeAtom(p, 0, 6, pos[0]);
  pos[1].x = -154.9;
  pos[1].y = 0;
  pos[1].z = 0;
  makeAtom(p, 1, 6, pos[1]);
  pos[2].x = 154.9;
  pos[2].y = 0;
  pos[2].z = 0;
  makeAtom(p, 2, 6, pos[2]);
  makeBond(p, 0, 1, '1');
  makeBond(p, 0, 2, '1');
  makeVanDerWaals(p, 1, 2);
  endPart(p);
  generateStretches(p);
  generateBends(p);
  //printPart(stdout, p);
  fprintf(out, "s %f %f %f %f %f %f %f\n",
          pos[0].x,
          pos[0].y,
          pos[0].z,
          10.0,
          1.0, 0.0, 0.0);
  fprintf(out, "s %f %f %f %f %f %f %f\n",
          pos[1].x,
          pos[1].y,
          pos[1].z,
          10.0,
          0.5, 0.0, 0.0);
  fprintf(out, "s %f %f %f %f %f %f %f\n",
          pos[0].x,
          pos[0].y,
          ZOFFSET,
          10.0,
          1.0, 0.0, 0.0);
  fprintf(out, "s %f %f %f %f %f %f %f\n",
          pos[1].x,
          pos[1].y,
          ZOFFSET,
          10.0,
          0.5, 0.0, 0.0);
  for (a=A_MIN; a<A_MAX; a+=A_INCR) {
    for (b=B_MIN; b<B_MAX; b+=B_INCR) {
      x = X(a, b);
      y = Y(a, b);
      pos[2].x = x;
      pos[2].y = y;

      x1 = X(a, b-B_INCR);
      y1 = Y(a, b-B_INCR);
      if (b == B_MIN) {
        pos[2].x = x1;
        pos[2].y = y1;
        prevB_potential = calculatePotential(p, pos) * POTENTIAL_SCALE;
      }
      pos[2].x = x;
      pos[2].y = y;
      potential = calculatePotential(p, pos) * POTENTIAL_SCALE;
      x2 = X(a-A_INCR, b);
      y2 = Y(a-A_INCR, b);
      pos[2].x = x2;
      pos[2].y = y2;
      prevA_potential = calculatePotential(p, pos) * POTENTIAL_SCALE;

      if (potential < POTENTIAL_CUTOFF) {
        red1 = 0;
      } else {
        red1 = 1;
        potential = POTENTIAL_CUTOFF;
      }
      
      if (prevA_potential > POTENTIAL_CUTOFF) {
        red2 = 1;
        prevA_potential = POTENTIAL_CUTOFF;
      } else {
        red2 = red1;
      }
      fprintf(out, "l %f %f %f %f %f %f %s\n",
              x2, y2, prevA_potential,
              x, y, potential,
              red2 ? "1 0 0" : "0 0 1");

      if (prevB_potential > POTENTIAL_CUTOFF) {
        red2 = 1;
        prevB_potential = POTENTIAL_CUTOFF;
      } else {
        red2 = red1;
      }
      fprintf(out, "l %f %f %f %f %f %f %s\n",
              x1, y1, prevB_potential,
              x, y, potential,
              red2 ? "1 0 0" : "0 0 1");

      prevB_potential = potential;
      
      calculateGradient(p, pos, force);
      
      flen = vlen(force[2]);
      if (flen > FORCE_CUTOFF) {
        vmulc(force[2], FORCE_CUTOFF / flen);
        red = 1;
        grn = 0;
        blu = 0;
      } else {
        red = 1;
        grn = 1;
        blu = 1;
      }
      
      fprintf(out, "l %f %f %f %f %f %f %f %f %f\n",
              x, y, ZOFFSET,
              x + (force[2].x * FORCE_SCALE),
              y + (force[2].y * FORCE_SCALE),
              ZOFFSET,
              red, grn, blu);
      fprintf(out, "l %f %f %f %f %f %f %f %f %f\n",
              x, y, ZOFFSET+ZTICK,
              x, y, ZOFFSET,
              1.0, 1.0, blu);
      
    }
  }
  fprintf(out, "f force\n");
  fclose(out);
}
