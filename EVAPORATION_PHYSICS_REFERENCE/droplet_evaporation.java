/*
 * droplet_evaporation.java
 */

import com.comsol.model.*;
import com.comsol.model.util.*;

/** Model exported on Aug 15 2025, 16:26 by COMSOL 6.3.0.290. */
public class droplet_evaporation {

  public static Model run() {
    Model model = ModelUtil.create("Model");

    model.modelPath("E:\\2025\\WORK\\EUV_LITHOGRAPHY\\Mie_Theory\\2d_Model\\TO-DELETE-LATER");

    model.label("droplet_evaporation.mph");

    model.title("Droplet Evaporation on Solid Substrate");

    model
         .description("Droplet evaporation is ubiquitous in everyday life, and is essential in many industrial processes such as ink-jet printing, cleaning or coating of surfaces, and phase change heat transfer.\n\nIn this model, a water droplet placed on a solid substrate evaporates in air. We solve the equations for two-phase flow coupled with heat transfer and transport of water vapor. The model is first verified against isothermal analytical solution, and then extended to include nonisothermal effects.");

    model.param().set("D", "0.282 [cm^2/s]", "diffusion coefficient of water vapor in air");
    model.param().set("LH", "2264 [kJ/kg]", "latent heat of vaporization");
    model.param().set("A", "8.07131", "constant for Antoine equation");
    model.param().set("B", "1730.63", "constant for Antoine equation");
    model.param().set("C", "233.426", "constant for Antoine equation");
    model.param().set("Rs", "461.5[J/kg/K]", "specific gas constant");
    model.param().set("Mw", "18e-3[kg/mol]", "molecular weight");
    model.param().set("DeltaT", "15 [K]", "substrate heating");
    model.param().set("R0", "1[mm]", "initial drop radius");
    model.param().set("H0", "1[mm]", "substrate thickness");
    model.param().set("sigma", "70[mN/m]", "surface tension");
    model.param().set("T_iso", "293.15 [K]", "isothermal case - temperature");
    model.param()
         .set("Psat_iso", "10^(A-B/(C+(T_iso[1/K]-273.15)))[mmHg]", "isothermal case - saturation vapor pressure");
    model.param().set("rhosat_iso", "Psat_iso/Rs/T_iso", "isothermal case - saturation vapor density");
    model.param().set("rhow_iso", "comp1.mat2.def.rho(T_iso)", "isothermal case - water density");

    model.component().create("comp1", true);

    model.component("comp1").geom().create("geom1", 2);

    model.result().table().create("evl3", "Table");

    model.component("comp1").func().create("step1", "Step");
    model.component("comp1").func("step1").set("location", 0.05);

    model.component("comp1").geom("geom1").axisymmetric(true);

    model.component("comp1").mesh().create("mesh1");

    model.component("comp1").geom("geom1").create("c1", "Circle");
    model.component("comp1").geom("geom1").feature("c1").set("r", "20*R0");
    model.component("comp1").geom("geom1").feature("c1").set("angle", 90);
    model.component("comp1").geom("geom1").feature("c1").set("layername", new String[]{"Layer 1"});
    model.component("comp1").geom("geom1").feature("c1").setIndex("layer", "R0", 0);
    model.component("comp1").geom("geom1").create("r1", "Rectangle");
    model.component("comp1").geom("geom1").feature("r1").set("size", new String[]{"5*R0", "H0"});
    model.component("comp1").geom("geom1").feature("r1").set("layerleft", true);
    model.component("comp1").geom("geom1").feature("r1").set("layerbottom", false);
    model.component("comp1").geom("geom1").create("c2", "Circle");
    model.component("comp1").geom("geom1").feature("c2").set("r", "R0");
    model.component("comp1").geom("geom1").feature("c2").set("angle", 90);
    model.component("comp1").geom("geom1").feature("c2").set("pos", new String[]{"0", "H0"});
    model.component("comp1").geom("geom1").run();

    model.component("comp1").variable().create("var1");
    model.component("comp1").variable("var1")
         .set("Psat", "10^(A-B/(C+(T[1/K]-273.15)))[mmHg]", "saturation vapor pressure");
    model.component("comp1").variable("var1").set("rhosat", "Psat/Rs/T", "saturation vapor density");
    model.component("comp1").variable("var1").set("csat", "rhosat/Mw", "saturation vapor concentration");
    model.component("comp1").variable("var1")
         .set("R_iso", "sqrt(R0^2-2*(D*rhosat_iso/rhow_iso)*t)", "analytical solution - radius");
    model.component("comp1").variable("var1").set("V_iso", "2/3*pi*R_iso^3", "analytical solution - volume");
    model.component("comp1").variable("var1")
         .set("J", "if(r<h/1e3,-Mw*D*(nr*cr+nz*cz),Mw*c_lm*1[mol/m/s]/(2*pi*r))", "evaporative mass flux");

    model.view().create("view2", 3);
    model.view().create("view3", 3);
    model.view().create("view4", 3);

    model.component("comp1").material().create("mat1", "Common");
    model.component("comp1").material().create("mat2", "Common");
    model.component("comp1").material("mat1").selection().set(2, 3, 4);
    model.component("comp1").material("mat1").propertyGroup("def").func().create("eta", "Piecewise");
    model.component("comp1").material("mat1").propertyGroup("def").func().create("Cp", "Piecewise");
    model.component("comp1").material("mat1").propertyGroup("def").func().create("rho", "Analytic");
    model.component("comp1").material("mat1").propertyGroup("def").func().create("k", "Piecewise");
    model.component("comp1").material("mat1").propertyGroup("def").func().create("cs", "Analytic");
    model.component("comp1").material("mat1").propertyGroup("def").func().create("an1", "Analytic");
    model.component("comp1").material("mat1").propertyGroup("def").func().create("an2", "Analytic");
    model.component("comp1").material("mat1").propertyGroup()
         .create("RefractiveIndex", "RefractiveIndex", "Refractive index");
    model.component("comp1").material("mat1").propertyGroup()
         .create("NonlinearModel", "NonlinearModel", "Nonlinear model");
    model.component("comp1").material("mat1").propertyGroup().create("idealGas", "idealGas", "Ideal gas");
    model.component("comp1").material("mat1").propertyGroup("idealGas").func().create("Cp", "Piecewise");
    model.component("comp1").material("mat2").selection().set(2);
    model.component("comp1").material("mat2").propertyGroup("def").func().create("eta", "Piecewise");
    model.component("comp1").material("mat2").propertyGroup("def").func().create("Cp", "Piecewise");
    model.component("comp1").material("mat2").propertyGroup("def").func().create("rho", "Piecewise");
    model.component("comp1").material("mat2").propertyGroup("def").func().create("k", "Piecewise");
    model.component("comp1").material("mat2").propertyGroup("def").func().create("cs", "Interpolation");
    model.component("comp1").material("mat2").propertyGroup("def").func().create("an1", "Analytic");
    model.component("comp1").material("mat2").propertyGroup("def").func().create("an2", "Analytic");
    model.component("comp1").material("mat2").propertyGroup("def").func().create("an3", "Analytic");

    model.component("comp1").cpl().create("intop1", "Integration");
    model.component("comp1").cpl().create("intop2", "Integration");
    model.component("comp1").cpl("intop1").selection().set(2);
    model.component("comp1").cpl("intop2").selection().geom("geom1", 0);
    model.component("comp1").cpl("intop2").selection().set(6);

    model.component("comp1").coordSystem().create("ie1", "InfiniteElement");
    model.component("comp1").coordSystem("ie1").selection().set(4);

    model.component("comp1").common().create("free1", "DeformingDomain");
    model.component("comp1").common().create("pnmd1", "PrescribedNormalMeshDisplacement");
    model.component("comp1").common().create("fix1", "FixedBoundary");
    model.component("comp1").common().create("disp2", "PrescribedMeshDisplacement");
    model.component("comp1").common().create("disp3", "PrescribedMeshDisplacement");
    model.component("comp1").common("free1").selection().set(2, 3);
    model.component("comp1").common("pnmd1").selection().set(3, 4, 5, 7, 8, 9);
    model.component("comp1").common("fix1").selection().set(8, 9, 12);
    model.component("comp1").common("disp2").selection().set(2, 4);
    model.component("comp1").common("disp3").selection().set(7);

    model.component("comp1").physics().create("spf", "LaminarFlow", "geom1");
    model.component("comp1").physics("spf").selection().set(2, 3);
    model.component("comp1").physics("spf").create("init2", "init", 2);
    model.component("comp1").physics("spf").feature("init2").selection().set(2);
    model.component("comp1").physics("spf").create("ffi1", "FluidFluidInterface", 1);
    model.component("comp1").physics("spf").feature("ffi1").selection().set(11);
    model.component("comp1").physics("spf").create("open1", "OpenBoundary", 1);
    model.component("comp1").physics("spf").feature("open1").selection().set(12);
    model.component("comp1").physics("spf").create("wallbc2", "WallBC", 1);
    model.component("comp1").physics("spf").feature("wallbc2").selection().set(8, 9);
    model.component("comp1").physics().create("tds", "DilutedSpecies", "geom1");
    model.component("comp1").physics("tds").selection().set(3, 4);
    model.component("comp1").physics("tds").create("cdm2", "Fluid", 2);
    model.component("comp1").physics("tds").feature("cdm2").selection().set(4);
    model.component("comp1").physics("tds").create("conc1", "Concentration", 1);
    model.component("comp1").physics("tds").feature("conc1").selection().set(11);
    model.component("comp1").physics("tds").create("conc2", "Concentration", 1);
    model.component("comp1").physics("tds").feature("conc2").selection().set(13);
    model.component("comp1").physics().create("ht", "HeatTransferInSolidsAndFluids", "geom1");
    model.component("comp1").physics("ht").selection().set(2, 3, 4);
    model.component("comp1").physics("ht").feature("fluid1").selection().set(2, 3);
    model.component("comp1").physics("ht").create("fluid2", "FluidHeatTransferModel", 2);
    model.component("comp1").physics("ht").feature("fluid2").selection().set(4);
    model.component("comp1").physics("ht").create("temp1", "TemperatureBoundary", 1);
    model.component("comp1").physics("ht").feature("temp1").selection().set(2, 4, 7, 8);
    model.component("comp1").physics("ht").create("bhs1", "BoundaryHeatSource", 1);
    model.component("comp1").physics("ht").feature("bhs1").selection().set(11);
    model.component("comp1").physics("ht").create("temp2", "TemperatureBoundary", 1);
    model.component("comp1").physics("ht").feature("temp2").selection().set(13);
    model.component("comp1").physics().create("ge", "GlobalEquations", "geom1");
    model.component("comp1").physics("ge").feature("ge1").set("DependentVariableQuantity", "none");

    model.component("comp1").multiphysics().create("nitf1", "NonIsothermalFlow", 2);
    model.component("comp1").multiphysics().create("rfd1", "ReactingFlowDS", 2);

    model.component("comp1").mesh("mesh1").create("map2", "Map");
    model.component("comp1").mesh("mesh1").create("ftri1", "FreeTri");
    model.component("comp1").mesh("mesh1").feature("map2").selection().geom("geom1", 2);
    model.component("comp1").mesh("mesh1").feature("map2").selection().set(4);
    model.component("comp1").mesh("mesh1").feature("map2").create("dis1", "Distribution");
    model.component("comp1").mesh("mesh1").feature("map2").feature("dis1").selection().set(6, 10);
    model.component("comp1").mesh("mesh1").feature("ftri1").selection().geom("geom1", 2);
    model.component("comp1").mesh("mesh1").feature("ftri1").selection().set(2, 3);
    model.component("comp1").mesh("mesh1").feature("ftri1").create("size1", "Size");
    model.component("comp1").mesh("mesh1").feature("ftri1").feature("size1").selection().geom("geom1", 1);
    model.component("comp1").mesh("mesh1").feature("ftri1").feature("size1").selection().set(11);

    model.result().table("evl3").label("Evaluation 3D");
    model.result().table("evl3").comments("Interactive 3D values");

    model.component("comp1").view("view1").axis().set("xmin", -0.012359441258013248);
    model.component("comp1").view("view1").axis().set("xmax", 0.032359443604946136);
    model.component("comp1").view("view1").axis().set("ymin", -0.00966336764395237);
    model.component("comp1").view("view1").axis().set("ymax", 0.029663367196917534);
    model.view("view3").set("showgrid", false);

    model.component("comp1").material("mat1").label("Air");
    model.component("comp1").material("mat1").set("family", "air");
    model.component("comp1").material("mat1").propertyGroup("def").func("eta").set("arg", "T");
    model.component("comp1").material("mat1").propertyGroup("def").func("eta")
         .set("pieces", new String[][]{{"200.0", "1600.0", "-8.38278E-7+8.35717342E-8*T^1-7.69429583E-11*T^2+4.6437266E-14*T^3-1.06585607E-17*T^4"}});
    model.component("comp1").material("mat1").propertyGroup("def").func("eta").set("argunit", "K");
    model.component("comp1").material("mat1").propertyGroup("def").func("eta").set("fununit", "Pa*s");
    model.component("comp1").material("mat1").propertyGroup("def").func("Cp").set("arg", "T");
    model.component("comp1").material("mat1").propertyGroup("def").func("Cp")
         .set("pieces", new String[][]{{"200.0", "1600.0", "1047.63657-0.372589265*T^1+9.45304214E-4*T^2-6.02409443E-7*T^3+1.2858961E-10*T^4"}});
    model.component("comp1").material("mat1").propertyGroup("def").func("Cp").set("argunit", "K");
    model.component("comp1").material("mat1").propertyGroup("def").func("Cp").set("fununit", "J/(kg*K)");
    model.component("comp1").material("mat1").propertyGroup("def").func("rho")
         .set("expr", "pA*0.02897/R_const[K*mol/J]/T");
    model.component("comp1").material("mat1").propertyGroup("def").func("rho").set("args", new String[]{"pA", "T"});
    model.component("comp1").material("mat1").propertyGroup("def").func("rho").set("fununit", "kg/m^3");
    model.component("comp1").material("mat1").propertyGroup("def").func("rho")
         .set("argunit", new String[]{"Pa", "K"});
    model.component("comp1").material("mat1").propertyGroup("def").func("rho")
         .set("plotaxis", new String[]{"on", "on"});
    model.component("comp1").material("mat1").propertyGroup("def").func("rho")
         .set("plotfixedvalue", new String[]{"0", "0"});
    model.component("comp1").material("mat1").propertyGroup("def").func("rho")
         .set("plotargs", new String[][]{{"pA", "0", "1"}, {"T", "0", "1"}});
    model.component("comp1").material("mat1").propertyGroup("def").func("k").set("arg", "T");
    model.component("comp1").material("mat1").propertyGroup("def").func("k")
         .set("pieces", new String[][]{{"200.0", "1600.0", "-0.00227583562+1.15480022E-4*T^1-7.90252856E-8*T^2+4.11702505E-11*T^3-7.43864331E-15*T^4"}});
    model.component("comp1").material("mat1").propertyGroup("def").func("k").set("argunit", "K");
    model.component("comp1").material("mat1").propertyGroup("def").func("k").set("fununit", "W/(m*K)");
    model.component("comp1").material("mat1").propertyGroup("def").func("cs")
         .set("expr", "sqrt(1.4*R_const[K*mol/J]/0.02897*T)");
    model.component("comp1").material("mat1").propertyGroup("def").func("cs").set("args", new String[]{"T"});
    model.component("comp1").material("mat1").propertyGroup("def").func("cs").set("fununit", "m/s");
    model.component("comp1").material("mat1").propertyGroup("def").func("cs").set("argunit", new String[]{"K"});
    model.component("comp1").material("mat1").propertyGroup("def").func("cs")
         .set("plotargs", new String[][]{{"T", "273.15", "373.15"}});
    model.component("comp1").material("mat1").propertyGroup("def").func("an1").set("funcname", "alpha_p");
    model.component("comp1").material("mat1").propertyGroup("def").func("an1")
         .set("expr", "-1/rho(pA,T)*d(rho(pA,T),T)");
    model.component("comp1").material("mat1").propertyGroup("def").func("an1").set("args", new String[]{"pA", "T"});
    model.component("comp1").material("mat1").propertyGroup("def").func("an1").set("fununit", "1/K");
    model.component("comp1").material("mat1").propertyGroup("def").func("an1")
         .set("argunit", new String[]{"Pa", "K"});
    model.component("comp1").material("mat1").propertyGroup("def").func("an1")
         .set("plotaxis", new String[]{"off", "on"});
    model.component("comp1").material("mat1").propertyGroup("def").func("an1")
         .set("plotfixedvalue", new String[]{"0", "0"});
    model.component("comp1").material("mat1").propertyGroup("def").func("an1")
         .set("plotargs", new String[][]{{"pA", "101325", "101325"}, {"T", "273.15", "373.15"}});
    model.component("comp1").material("mat1").propertyGroup("def").func("an2").set("funcname", "muB");
    model.component("comp1").material("mat1").propertyGroup("def").func("an2").set("expr", "0.6*eta(T)");
    model.component("comp1").material("mat1").propertyGroup("def").func("an2").set("args", new String[]{"T"});
    model.component("comp1").material("mat1").propertyGroup("def").func("an2").set("fununit", "Pa*s");
    model.component("comp1").material("mat1").propertyGroup("def").func("an2").set("argunit", new String[]{"K"});
    model.component("comp1").material("mat1").propertyGroup("def").func("an2")
         .set("plotargs", new String[][]{{"T", "200", "1600"}});
    model.component("comp1").material("mat1").propertyGroup("def")
         .set("thermalexpansioncoefficient", new String[]{"alpha_p(pA,T)", "0", "0", "0", "alpha_p(pA,T)", "0", "0", "0", "alpha_p(pA,T)"});
    model.component("comp1").material("mat1").propertyGroup("def").set("molarmass", "0.02897[kg/mol]");
    model.component("comp1").material("mat1").propertyGroup("def").set("bulkviscosity", "muB(T)");
    model.component("comp1").material("mat1").propertyGroup("def")
         .set("relpermeability", new String[]{"1", "0", "0", "0", "1", "0", "0", "0", "1"});
    model.component("comp1").material("mat1").propertyGroup("def")
         .set("relpermittivity", new String[]{"1", "0", "0", "0", "1", "0", "0", "0", "1"});
    model.component("comp1").material("mat1").propertyGroup("def").set("dynamicviscosity", "eta(T)");
    model.component("comp1").material("mat1").propertyGroup("def").set("ratioofspecificheat", "1.4");
    model.component("comp1").material("mat1").propertyGroup("def")
         .set("electricconductivity", new String[]{"0[S/m]", "0", "0", "0", "0[S/m]", "0", "0", "0", "0[S/m]"});
    model.component("comp1").material("mat1").propertyGroup("def").set("heatcapacity", "Cp(T)");
    model.component("comp1").material("mat1").propertyGroup("def").set("density", "rho(pA,T)");
    model.component("comp1").material("mat1").propertyGroup("def")
         .set("thermalconductivity", new String[]{"k(T)", "0", "0", "0", "k(T)", "0", "0", "0", "k(T)"});
    model.component("comp1").material("mat1").propertyGroup("def").set("soundspeed", "cs(T)");
    model.component("comp1").material("mat1").propertyGroup("def").addInput("temperature");
    model.component("comp1").material("mat1").propertyGroup("def").addInput("pressure");
    model.component("comp1").material("mat1").propertyGroup("RefractiveIndex")
         .set("n", new String[]{"1", "0", "0", "0", "1", "0", "0", "0", "1"});
    model.component("comp1").material("mat1").propertyGroup("NonlinearModel").set("BA", "(def.gamma+1)/2");
    model.component("comp1").material("mat1").propertyGroup("idealGas").func("Cp").label("Piecewise 2");
    model.component("comp1").material("mat1").propertyGroup("idealGas").func("Cp").set("arg", "T");
    model.component("comp1").material("mat1").propertyGroup("idealGas").func("Cp")
         .set("pieces", new String[][]{{"200.0", "1600.0", "1047.63657-0.372589265*T^1+9.45304214E-4*T^2-6.02409443E-7*T^3+1.2858961E-10*T^4"}});
    model.component("comp1").material("mat1").propertyGroup("idealGas").func("Cp").set("argunit", "K");
    model.component("comp1").material("mat1").propertyGroup("idealGas").func("Cp").set("fununit", "J/(kg*K)");
    model.component("comp1").material("mat1").propertyGroup("idealGas").set("Rs", "R_const/Mn");
    model.component("comp1").material("mat1").propertyGroup("idealGas").set("heatcapacity", "Cp(T)");
    model.component("comp1").material("mat1").propertyGroup("idealGas").set("ratioofspecificheat", "1.4");
    model.component("comp1").material("mat1").propertyGroup("idealGas").set("molarmass", "0.02897");
    model.component("comp1").material("mat1").propertyGroup("idealGas").addInput("temperature");
    model.component("comp1").material("mat1").propertyGroup("idealGas").addInput("pressure");
    model.component("comp1").material("mat2").label("Water, liquid");
    model.component("comp1").material("mat2").set("family", "water");
    model.component("comp1").material("mat2").propertyGroup("def").func("eta").set("arg", "T");
    model.component("comp1").material("mat2").propertyGroup("def").func("eta")
         .set("pieces", new String[][]{{"273.15", "413.15", "1.3799566804-0.021224019151*T^1+1.3604562827E-4*T^2-4.6454090319E-7*T^3+8.9042735735E-10*T^4-9.0790692686E-13*T^5+3.8457331488E-16*T^6"}, {"413.15", "553.75", "0.00401235783-2.10746715E-5*T^1+3.85772275E-8*T^2-2.39730284E-11*T^3"}});
    model.component("comp1").material("mat2").propertyGroup("def").func("eta").set("argunit", "K");
    model.component("comp1").material("mat2").propertyGroup("def").func("eta").set("fununit", "Pa*s");
    model.component("comp1").material("mat2").propertyGroup("def").func("Cp").set("arg", "T");
    model.component("comp1").material("mat2").propertyGroup("def").func("Cp")
         .set("pieces", new String[][]{{"273.15", "553.75", "12010.1471-80.4072879*T^1+0.309866854*T^2-5.38186884E-4*T^3+3.62536437E-7*T^4"}});
    model.component("comp1").material("mat2").propertyGroup("def").func("Cp").set("argunit", "K");
    model.component("comp1").material("mat2").propertyGroup("def").func("Cp").set("fununit", "J/(kg*K)");
    model.component("comp1").material("mat2").propertyGroup("def").func("rho").set("arg", "T");
    model.component("comp1").material("mat2").propertyGroup("def").func("rho").set("smooth", "contd1");
    model.component("comp1").material("mat2").propertyGroup("def").func("rho")
         .set("pieces", new String[][]{{"273.15", "293.15", "0.000063092789034*T^3-0.060367639882855*T^2+18.9229382407066*T-950.704055329848"}, {"293.15", "373.15", "0.000010335053319*T^3-0.013395065634452*T^2+4.969288832655160*T+432.257114008512"}});
    model.component("comp1").material("mat2").propertyGroup("def").func("rho").set("argunit", "K");
    model.component("comp1").material("mat2").propertyGroup("def").func("rho").set("fununit", "kg/m^3");
    model.component("comp1").material("mat2").propertyGroup("def").func("k").set("arg", "T");
    model.component("comp1").material("mat2").propertyGroup("def").func("k")
         .set("pieces", new String[][]{{"273.15", "553.75", "-0.869083936+0.00894880345*T^1-1.58366345E-5*T^2+7.97543259E-9*T^3"}});
    model.component("comp1").material("mat2").propertyGroup("def").func("k").set("argunit", "K");
    model.component("comp1").material("mat2").propertyGroup("def").func("k").set("fununit", "W/(m*K)");
    model.component("comp1").material("mat2").propertyGroup("def").func("cs")
         .set("table", new String[][]{{"273", "1403"}, 
         {"278", "1427"}, 
         {"283", "1447"}, 
         {"293", "1481"}, 
         {"303", "1507"}, 
         {"313", "1526"}, 
         {"323", "1541"}, 
         {"333", "1552"}, 
         {"343", "1555"}, 
         {"353", "1555"}, 
         {"363", "1550"}, 
         {"373", "1543"}});
    model.component("comp1").material("mat2").propertyGroup("def").func("cs").set("interp", "piecewisecubic");
    model.component("comp1").material("mat2").propertyGroup("def").func("cs").set("fununit", new String[]{"m/s"});
    model.component("comp1").material("mat2").propertyGroup("def").func("cs").set("argunit", new String[]{"K"});
    model.component("comp1").material("mat2").propertyGroup("def").func("an1").set("funcname", "alpha_p");
    model.component("comp1").material("mat2").propertyGroup("def").func("an1").set("expr", "-1/rho(T)*d(rho(T),T)");
    model.component("comp1").material("mat2").propertyGroup("def").func("an1").set("args", new String[]{"T"});
    model.component("comp1").material("mat2").propertyGroup("def").func("an1").set("fununit", "1/K");
    model.component("comp1").material("mat2").propertyGroup("def").func("an1").set("argunit", new String[]{"K"});
    model.component("comp1").material("mat2").propertyGroup("def").func("an1")
         .set("plotargs", new String[][]{{"T", "273.15", "373.15"}});
    model.component("comp1").material("mat2").propertyGroup("def").func("an2").set("funcname", "gamma_w");
    model.component("comp1").material("mat2").propertyGroup("def").func("an2")
         .set("expr", "1+(T/Cp(T))*(alpha_p(T)*cs(T))^2");
    model.component("comp1").material("mat2").propertyGroup("def").func("an2").set("args", new String[]{"T"});
    model.component("comp1").material("mat2").propertyGroup("def").func("an2").set("fununit", "1");
    model.component("comp1").material("mat2").propertyGroup("def").func("an2").set("argunit", new String[]{"K"});
    model.component("comp1").material("mat2").propertyGroup("def").func("an2")
         .set("plotargs", new String[][]{{"T", "273.15", "373.15"}});
    model.component("comp1").material("mat2").propertyGroup("def").func("an3").set("funcname", "muB");
    model.component("comp1").material("mat2").propertyGroup("def").func("an3").set("expr", "2.79*eta(T)");
    model.component("comp1").material("mat2").propertyGroup("def").func("an3").set("args", new String[]{"T"});
    model.component("comp1").material("mat2").propertyGroup("def").func("an3").set("fununit", "Pa*s");
    model.component("comp1").material("mat2").propertyGroup("def").func("an3").set("argunit", new String[]{"K"});
    model.component("comp1").material("mat2").propertyGroup("def").func("an3")
         .set("plotargs", new String[][]{{"T", "273.15", "553.75"}});
    model.component("comp1").material("mat2").propertyGroup("def")
         .set("thermalexpansioncoefficient", new String[]{"alpha_p(T)", "0", "0", "0", "alpha_p(T)", "0", "0", "0", "alpha_p(T)"});
    model.component("comp1").material("mat2").propertyGroup("def").set("bulkviscosity", "muB(T)");
    model.component("comp1").material("mat2").propertyGroup("def").set("dynamicviscosity", "eta(T)");
    model.component("comp1").material("mat2").propertyGroup("def").set("ratioofspecificheat", "gamma_w(T)");
    model.component("comp1").material("mat2").propertyGroup("def")
         .set("electricconductivity", new String[]{"5.5e-6[S/m]", "0", "0", "0", "5.5e-6[S/m]", "0", "0", "0", "5.5e-6[S/m]"});
    model.component("comp1").material("mat2").propertyGroup("def").set("heatcapacity", "Cp(T)");
    model.component("comp1").material("mat2").propertyGroup("def").set("density", "rho(T)");
    model.component("comp1").material("mat2").propertyGroup("def")
         .set("thermalconductivity", new String[]{"k(T)", "0", "0", "0", "k(T)", "0", "0", "0", "k(T)"});
    model.component("comp1").material("mat2").propertyGroup("def").set("soundspeed", "cs(T)");
    model.component("comp1").material("mat2").propertyGroup("def").addInput("temperature");

    model.component("comp1").cpl("intop1").label("Volume Integration");
    model.component("comp1").cpl("intop1").set("axisym", true);
    model.component("comp1").cpl("intop2").label("Mesh Displacement");

    model.component("comp1").common("disp2")
         .set("prescribedMeshDisplacement", new String[]{"mesh_disp*Rg/R0", "0", "0"});
    model.component("comp1").common("disp3")
         .set("prescribedMeshDisplacement", new String[]{"mesh_disp*(Rg-5*R0)/(-4*R0)", "0", "0"});

    model.component("comp1").physics("spf").prop("PhysicalModelProperty")
         .set("Compressibility", "WeaklyCompressible");
    model.component("comp1").physics("spf").prop("PhysicalModelProperty")
         .set("PorousWallTreatment", "PorousResolvedWall");
    model.component("comp1").physics("spf").prop("TurbulenceModelProperty").set("WallTreatment", "WallFunctions");
    model.component("comp1").physics("spf").prop("TurbulenceModelProperty").set("Cs", 0.01);
    model.component("comp1").physics("spf").prop("ConsistentStabilization").set("CrosswindDiffusion", false);
    model.component("comp1").physics("spf").feature("fp1").set("mu_init_app", "spf.mu0");
    model.component("comp1").physics("spf").feature("wallbc1").set("BoundaryCondition", "NavierSlip");
    model.component("comp1").physics("spf").feature("dcont1").set("continuityConditions", "velocityAndStress");
    model.component("comp1").physics("spf").feature("dcont1").set("pairDisconnect", true);
    model.component("comp1").physics("spf").feature("dcont1").label("Continuity");
    model.component("comp1").physics("spf").feature("init2").set("p_init", "2*sigma/R0");
    model.component("comp1").physics("spf").feature("ffi1").set("Mf", "J");
    model.component("comp1").physics("spf").feature("ffi1").set("SurfaceTensionCoefficient", "userdef");
    model.component("comp1").physics("spf").feature("ffi1").set("sigma", "sigma");
    model.component("comp1").physics("tds").feature("sp1").label("Species Properties");
    model.component("comp1").physics("tds").feature("cdm1").set("u_src", "root.comp1.u");
    model.component("comp1").physics("tds").feature("cdm1")
         .set("D_c", new String[][]{{"D"}, {"0"}, {"0"}, {"0"}, {"D"}, {"0"}, {"0"}, {"0"}, {"D"}});
    model.component("comp1").physics("tds").feature("dcont1").set("pairDisconnect", true);
    model.component("comp1").physics("tds").feature("dcont1").label("Continuity");
    model.component("comp1").physics("tds").feature("cdm2")
         .set("D_c", new String[][]{{"D"}, {"0"}, {"0"}, {"0"}, {"D"}, {"0"}, {"0"}, {"0"}, {"D"}});
    model.component("comp1").physics("tds").feature("conc1").set("species", true);
    model.component("comp1").physics("tds").feature("conc1").set("c0", "csat");
    model.component("comp1").physics("tds").feature("conc1").set("constraintOptions", "weakConstraints");
    model.component("comp1").physics("tds").feature("conc1").set("constraintType", "unidirectionalConstraint");
    model.component("comp1").physics("tds").feature("conc2").set("species", true);
    model.component("comp1").physics("ht").prop("RadiationSettings").set("functionResolution", 0);
    model.component("comp1").physics("ht").prop("RadiationSettings").set("opaque", "dfltopaque");
    model.component("comp1").physics("ht").feature("fluid1").set("gammaDumb", "from_mat");
    model.component("comp1").physics("ht").feature("fluid1").set("gamma_not_IG_mat", "from_mat");
    model.component("comp1").physics("ht").feature("fluid1").set("fluidType", "gasLiquid");
    model.component("comp1").physics("ht").feature("dcont1").set("pairDisconnect", true);
    model.component("comp1").physics("ht").feature("dcont1").label("Continuity");
    model.component("comp1").physics("ht").feature("fluid2").set("gammaDumb", "from_mat");
    model.component("comp1").physics("ht").feature("fluid2").set("gamma_not_IG_mat", "from_mat");
    model.component("comp1").physics("ht").feature("fluid2").set("minput_temperature_src", "root.comp1.T");
    model.component("comp1").physics("ht").feature("fluid2").set("editModelInputs", true);
    model.component("comp1").physics("ht").feature("temp1").set("T0", "293.15[K] + DeltaT*step1(t[1/s])");
    model.component("comp1").physics("ht").feature("bhs1").set("Qb_input", "-J*LH");
    model.component("comp1").physics("ge").feature("ge1").set("name", "mesh_disp");
    model.component("comp1").physics("ge").feature("ge1").set("equation", "mesh_dispt - intop2(spf.vn)");
    model.component("comp1").physics("ge").feature("ge1").set("SourceTermQuantity", "none");
    model.component("comp1").physics("ge").feature("ge1").set("CustomSourceTermUnit", "m/s");

    model.component("comp1").mesh("mesh1").feature("size").set("hauto", 2);
    model.component("comp1").mesh("mesh1").feature("map2").label("Mapped 1");
    model.component("comp1").mesh("mesh1").feature("ftri1").feature("size1").set("custom", "on");
    model.component("comp1").mesh("mesh1").feature("ftri1").feature("size1").set("hmax", "R0/100");
    model.component("comp1").mesh("mesh1").feature("ftri1").feature("size1").set("hmaxactive", true);
    model.component("comp1").mesh("mesh1").feature("ftri1").feature("size1").set("hmin", 9.0E-6);
    model.component("comp1").mesh("mesh1").feature("ftri1").feature("size1").set("hgrad", 1.01);

    return model;
  }

  public static Model run2(Model model) {
    model.component("comp1").mesh("mesh1").feature("ftri1").feature("size1").set("hgradactive", true);
    model.component("comp1").mesh("mesh1").feature("ftri1").feature("size1").set("hminactive", false);
    model.component("comp1").mesh("mesh1").run();

    model.study().create("std1");
    model.study("std1").create("time", "Transient");
    model.study("std1").feature("time")
         .set("activate", new String[]{"spf", "on", "tds", "on", "ht", "off", "ge", "on", "frame:spatial1", "on", 
         "frame:material1", "on"});
    model.study("std1").feature("time").set("activateCoupling", new String[]{"nitf1", "off", "rfd1", "on"});
    model.study().create("std2");
    model.study("std2").create("time", "Transient");

    model.sol().create("sol1");
    model.sol("sol1").attach("std1");
    model.sol("sol1").create("st1", "StudyStep");
    model.sol("sol1").create("v1", "Variables");
    model.sol("sol1").create("t1", "Time");
    model.sol("sol1").feature("t1").create("tp1", "TimeParametric");
    model.sol("sol1").feature("t1").create("se1", "Segregated");
    model.sol("sol1").feature("t1").create("d1", "Direct");
    model.sol("sol1").feature("t1").create("d2", "Direct");
    model.sol("sol1").feature("t1").create("i1", "Iterative");
    model.sol("sol1").feature("t1").create("i2", "Iterative");
    model.sol("sol1").feature("t1").create("fc1", "FullyCoupled");
    model.sol("sol1").feature("t1").feature("se1").create("ss1", "SegregatedStep");
    model.sol("sol1").feature("t1").feature("se1").create("ss2", "SegregatedStep");
    model.sol("sol1").feature("t1").feature("se1").create("ss3", "SegregatedStep");
    model.sol("sol1").feature("t1").feature("se1").feature().remove("ssDef");
    model.sol("sol1").feature("t1").feature("i1").create("dd1", "DomainDecomposition");
    model.sol("sol1").feature("t1").feature("i1").feature("dd1").feature("cs").create("d1", "Direct");
    model.sol("sol1").feature("t1").feature("i1").feature("dd1").feature("ds").create("d1", "Direct");
    model.sol("sol1").feature("t1").feature("i2").create("mg1", "Multigrid");
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("pr").create("va1", "Vanka");
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("po").create("va1", "Vanka");
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("cs").create("d1", "Direct");
    model.sol("sol1").feature("t1").feature().remove("fcDef");
    model.sol().create("sol2");
    model.sol("sol2").attach("std2");
    model.sol("sol2").create("st1", "StudyStep");
    model.sol("sol2").create("v1", "Variables");
    model.sol("sol2").create("t1", "Time");
    model.sol("sol2").feature("t1").create("se1", "Segregated");
    model.sol("sol2").feature("t1").create("d1", "Direct");
    model.sol("sol2").feature("t1").create("d2", "Direct");
    model.sol("sol2").feature("t1").create("d3", "Direct");
    model.sol("sol2").feature("t1").create("i1", "Iterative");
    model.sol("sol2").feature("t1").create("i2", "Iterative");
    model.sol("sol2").feature("t1").create("i3", "Iterative");
    model.sol("sol2").feature("t1").create("fc1", "FullyCoupled");
    model.sol("sol2").feature("t1").feature("se1").create("ss1", "SegregatedStep");
    model.sol("sol2").feature("t1").feature("se1").create("ss2", "SegregatedStep");
    model.sol("sol2").feature("t1").feature("se1").create("ss3", "SegregatedStep");
    model.sol("sol2").feature("t1").feature("se1").create("ss4", "SegregatedStep");
    model.sol("sol2").feature("t1").feature("se1").create("ll1", "LowerLimit");
    model.sol("sol2").feature("t1").feature("se1").feature().remove("ssDef");
    model.sol("sol2").feature("t1").feature("i1").create("dd1", "DomainDecomposition");
    model.sol("sol2").feature("t1").feature("i1").feature("dd1").feature("cs").create("d1", "Direct");
    model.sol("sol2").feature("t1").feature("i1").feature("dd1").feature("ds").create("d1", "Direct");
    model.sol("sol2").feature("t1").feature("i2").create("mg1", "Multigrid");
    model.sol("sol2").feature("t1").feature("i2").feature("mg1").feature("pr").create("so1", "SOR");
    model.sol("sol2").feature("t1").feature("i2").feature("mg1").feature("po").create("so1", "SOR");
    model.sol("sol2").feature("t1").feature("i2").feature("mg1").feature("cs").create("d1", "Direct");
    model.sol("sol2").feature("t1").feature("i3").create("mg1", "Multigrid");
    model.sol("sol2").feature("t1").feature("i3").feature("mg1").feature("pr").create("va1", "Vanka");
    model.sol("sol2").feature("t1").feature("i3").feature("mg1").feature("po").create("va1", "Vanka");
    model.sol("sol2").feature("t1").feature("i3").feature("mg1").feature("cs").create("d1", "Direct");
    model.sol("sol2").feature("t1").feature().remove("fcDef");

    model.result().configuration().create("prfu1", "PreferredUnits");
    model.result().dataset().create("rev1", "Revolve2D");
    model.result().dataset().create("dset3", "Solution");
    model.result().dataset().create("rev2", "Revolve2D");
    model.result().dataset("rev1").set("data", "dset2");
    model.result().dataset("dset3").set("solution", "sol2");
    model.result().dataset("dset3").selection().geom("geom1", 2);
    model.result().dataset("dset3").selection().set(1, 2);
    model.result().dataset("rev2").set("data", "dset3");
    model.result().create("pg1", "PlotGroup1D");
    model.result().create("pg9", "PlotGroup1D");
    model.result().create("pg2", "PlotGroup2D");
    model.result().create("pg5", "PlotGroup2D");
    model.result().create("pg8", "PlotGroup2D");
    model.result().create("pg11", "PlotGroup3D");
    model.result("pg1").create("glob1", "Global");
    model.result("pg1").create("glob2", "Global");
    model.result("pg1").feature("glob1").set("expr", new String[]{"intop1(1)"});
    model.result("pg1").feature("glob2").set("expr", new String[]{"V_iso"});
    model.result("pg9").set("data", "dset2");
    model.result("pg9").create("glob1", "Global");
    model.result("pg9").create("glob2", "Global");
    model.result("pg9").feature("glob1").set("expr", new String[]{"intop1(1)"});
    model.result("pg9").feature("glob2").set("data", "dset1");
    model.result("pg9").feature("glob2").set("expr", new String[]{"intop1(1)"});
    model.result("pg2").set("data", "dset2");
    model.result("pg2").create("surf1", "Surface");
    model.result("pg5").set("data", "dset2");
    model.result("pg5").create("surf1", "Surface");
    model.result("pg5").create("str1", "Streamline");
    model.result("pg5").feature("surf1").set("expr", "c");
    model.result("pg5").feature("str1").set("expr", new String[]{"tds.tflux_cr", "tds.tflux_cz"});
    model.result("pg8").set("data", "dset2");
    model.result("pg8").create("surf1", "Surface");
    model.result("pg8").feature("surf1").set("expr", "T");
    model.result("pg11").set("data", "rev2");
    model.result("pg11").create("surf1", "Surface");
    model.result("pg11").feature("surf1").set("expr", "T");

    model.nodeGroup().create("grp1", "Results");
    model.nodeGroup("grp1").set("type", "plotgroup");
    model.nodeGroup("grp1").placeAfter("plotgroup", "pg1");

    model.study("std1").label("Study 1 - Isothermal Case");
    model.study("std1").feature("time").set("tunit", "min");
    model.study("std1").feature("time").set("tlist", "range(0,0.5,16)");
    model.study("std1").feature("time").set("useparam", true);
    model.study("std1").feature("time").set("pname", new String[]{"DeltaT"});
    model.study("std1").feature("time").set("plistarr", new int[]{0});
    model.study("std1").feature("time").set("punit", new String[]{"K"});
    model.study("std2").label("Study 2 - Nonisothermal Case");
    model.study("std2").feature("time").set("tunit", "min");
    model.study("std2").feature("time").set("tlist", "range(0,0.5,8.5)");

    model.sol("sol1").feature("st1").label("Compile Equations: Time Dependent");
    model.sol("sol1").feature("v1").label("Dependent Variables 1.1");
    model.sol("sol1").feature("v1").set("clistctrl", new String[]{"tp1", "t1_t", "t1_timestep"});
    model.sol("sol1").feature("v1").set("cname", new String[]{"DeltaT", "t", "timestep"});
    model.sol("sol1").feature("v1").set("clist", new String[]{"0[K]", "{range(0, 0.5, 16)}[min]", "0.001[min]"});
    model.sol("sol1").feature("v1").feature("comp1_spatial_disp").set("scalemethod", "manual");
    model.sol("sol1").feature("v1").feature("comp1_spatial_disp").set("scaleval", 1.1906804777101203E-5);
    model.sol("sol1").feature("t1").label("Time-Dependent Solver 1.1");
    model.sol("sol1").feature("t1").set("tunit", "min");
    model.sol("sol1").feature("t1").set("tlist", "range(0,0.5,16)");
    model.sol("sol1").feature("t1").set("rtol", 0.005);
    model.sol("sol1").feature("t1").set("atolglobalfactor", 0.05);
    model.sol("sol1").feature("t1")
         .set("atolmethod", new String[]{"comp1_c", "global", "comp1_c_lm", "global", "comp1_nitf1_Uave", "global", "comp1_p", "scaled", "comp1_spatial_disp", "global", 
         "comp1_spatial_lm_nv", "global", "comp1_T", "global", "comp1_u", "global", "comp1_ODE1", "global"});
    model.sol("sol1").feature("t1")
         .set("atolfactor", new String[]{"comp1_c", "0.1", "comp1_c_lm", "0.1", "comp1_nitf1_Uave", "0.1", "comp1_p", "1", "comp1_spatial_disp", "0.1", 
         "comp1_spatial_lm_nv", "0.1", "comp1_T", "0.1", "comp1_u", "0.1", "comp1_ODE1", "0.1"});
    model.sol("sol1").feature("t1").set("initialstepbdfactive", true);
    model.sol("sol1").feature("t1").set("maxorder", 2);
    model.sol("sol1").feature("t1").set("stabcntrl", true);
    model.sol("sol1").feature("t1").set("bwinitstepfrac", 0.01);
    model.sol("sol1").feature("t1").set("estrat", "exclude");
    model.sol("sol1").feature("t1").feature("dDef").label("Direct 3");
    model.sol("sol1").feature("t1").feature("aDef").label("Advanced 1");
    model.sol("sol1").feature("t1").feature("aDef").set("cachepattern", true);
    model.sol("sol1").feature("t1").feature("tp1").label("Time Parametric 1.1");
    model.sol("sol1").feature("t1").feature("tp1").set("pname", new String[]{"DeltaT"});
    model.sol("sol1").feature("t1").feature("tp1").set("plistarr", new int[]{0});
    model.sol("sol1").feature("t1").feature("tp1").set("punit", new String[]{"K"});
    model.sol("sol1").feature("t1").feature("tp1").set("excludelsqvalues", false);
    model.sol("sol1").feature("t1").feature("se1").active(false);
    model.sol("sol1").feature("t1").feature("se1").label("Segregated 1.1");
    model.sol("sol1").feature("t1").feature("se1").set("ntolfact", 0.5);
    model.sol("sol1").feature("t1").feature("se1").set("segstabacc", "segaacc");
    model.sol("sol1").feature("t1").feature("se1").set("segaaccdim", 5);
    model.sol("sol1").feature("t1").feature("se1").set("segaaccmix", 0.9);
    model.sol("sol1").feature("t1").feature("se1").feature("ss1").label("Global ODEs and DAEs");
    model.sol("sol1").feature("t1").feature("se1").feature("ss1").set("segvar", new String[]{"comp1_ODE1"});
    model.sol("sol1").feature("t1").feature("se1").feature("ss1").set("subdamp", "0.8");
    model.sol("sol1").feature("t1").feature("se1").feature("ss1").set("subjtech", "onevery");
    model.sol("sol1").feature("t1").feature("se1").feature("ss2").label("Velocity u, Pressure p");
    model.sol("sol1").feature("t1").feature("se1").feature("ss2")
         .set("segvar", new String[]{"comp1_spatial_disp", "comp1_u", "comp1_p", "comp1_spatial_lm_nv"});
    model.sol("sol1").feature("t1").feature("se1").feature("ss2").set("linsolver", "d1");
    model.sol("sol1").feature("t1").feature("se1").feature("ss2").set("subdamp", "0.8");
    model.sol("sol1").feature("t1").feature("se1").feature("ss2").set("subjtech", "onevery");
    model.sol("sol1").feature("t1").feature("se1").feature("ss3").label("Concentration c");
    model.sol("sol1").feature("t1").feature("se1").feature("ss3")
         .set("segvar", new String[]{"comp1_c", "comp1_c_lm"});
    model.sol("sol1").feature("t1").feature("se1").feature("ss3").set("linsolver", "d2");
    model.sol("sol1").feature("t1").feature("se1").feature("ss3").set("subdamp", "0.8");
    model.sol("sol1").feature("t1").feature("se1").feature("ss3").set("subjtech", "once");
    model.sol("sol1").feature("t1").feature("d1").label("Direct, fluid flow variables (spf)");
    model.sol("sol1").feature("t1").feature("d1").set("linsolver", "pardiso");
    model.sol("sol1").feature("t1").feature("d1").set("pivotperturb", 1.0E-13);
    model.sol("sol1").feature("t1").feature("d2").active(true);
    model.sol("sol1").feature("t1").feature("d2").label("Direct, concentrations (tds)");
    model.sol("sol1").feature("t1").feature("d2").set("linsolver", "pardiso");
    model.sol("sol1").feature("t1").feature("d2").set("pivotperturb", 1.0E-13);
    model.sol("sol1").feature("t1").feature("i1").label("Multiplicative Schwarz, fluid flow variables (spf)");
    model.sol("sol1").feature("t1").feature("i1").set("maxlinit", 100);
    model.sol("sol1").feature("t1").feature("i1").set("rhob", 20);
    model.sol("sol1").feature("t1").feature("i1").feature("ilDef").label("Incomplete LU 1");
    model.sol("sol1").feature("t1").feature("i1").feature("dd1").label("Domain Decomposition (Schwarz) 1.1");
    model.sol("sol1").feature("t1").feature("i1").feature("dd1").set("ndom", 1);
    model.sol("sol1").feature("t1").feature("i1").feature("dd1").set("overlap", 2);
    model.sol("sol1").feature("t1").feature("i1").feature("dd1").set("meshoverlap", false);
    model.sol("sol1").feature("t1").feature("i1").feature("dd1").set("ddolhandling", "ddrestricted");
    model.sol("sol1").feature("t1").feature("i1").feature("dd1").set("usecoarse", "aggregation");
    model.sol("sol1").feature("t1").feature("i1").feature("dd1").set("maxcoarsedof", 10000);
    model.sol("sol1").feature("t1").feature("i1").feature("dd1").set("maxcoarsedofactive", true);
    model.sol("sol1").feature("t1").feature("i1").feature("dd1").set("usesmooth", false);
    model.sol("sol1").feature("t1").feature("i1").feature("dd1").feature("cs").label("Coarse Solver 1");
    model.sol("sol1").feature("t1").feature("i1").feature("dd1").feature("cs").feature("dDef").label("Direct 2");
    model.sol("sol1").feature("t1").feature("i1").feature("dd1").feature("cs").feature("d1").label("Direct 1.1");
    model.sol("sol1").feature("t1").feature("i1").feature("dd1").feature("cs").feature("d1")
         .set("linsolver", "pardiso");
    model.sol("sol1").feature("t1").feature("i1").feature("dd1").feature("cs").feature("d1")
         .set("pivotperturb", 1.0E-13);
    model.sol("sol1").feature("t1").feature("i1").feature("dd1").feature("ds").label("Domain Solver 1");
    model.sol("sol1").feature("t1").feature("i1").feature("dd1").feature("ds").feature("dDef").label("Direct 2");
    model.sol("sol1").feature("t1").feature("i1").feature("dd1").feature("ds").feature("d1").label("Direct 1.1");
    model.sol("sol1").feature("t1").feature("i1").feature("dd1").feature("ds").feature("d1")
         .set("linsolver", "pardiso");
    model.sol("sol1").feature("t1").feature("i1").feature("dd1").feature("ds").feature("d1")
         .set("pivotperturb", 1.0E-13);
    model.sol("sol1").feature("t1").feature("i2").label("AMG, concentrations (tds)");
    model.sol("sol1").feature("t1").feature("i2").set("maxlinit", 50);
    model.sol("sol1").feature("t1").feature("i2").feature("ilDef").label("Incomplete LU 1");
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").label("Multigrid 1.1");
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").set("prefun", "saamg");
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").set("maxcoarsedof", 50000);
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").set("nullspace", "constant");
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").set("usesmooth", false);
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("pr").label("Presmoother 1");
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("pr").feature("soDef").label("SOR 1");
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("pr").feature("va1").label("Vanka 1.1");
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("pr").feature("va1")
         .set("linesweeptype", "ssor");
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("pr").feature("va1").set("iter", 1);
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("pr").feature("va1")
         .set("vankavars", new String[]{"comp1_c_lm"});
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("pr").feature("va1")
         .set("vankasolv", "stored");
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("pr").feature("va1")
         .set("approxvanka", true);
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("pr").feature("va1")
         .set("vankadirectmaxsize", 1000);
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("pr").feature("va1").set("relax", 0.5);
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("po").label("Postsmoother 1");
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("po").feature("soDef").label("SOR 1");
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("po").feature("va1").label("Vanka 1.1");
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("po").feature("va1")
         .set("linesweeptype", "ssor");
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("po").feature("va1").set("iter", 1);
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("po").feature("va1")
         .set("vankavars", new String[]{"comp1_c_lm"});
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("po").feature("va1")
         .set("vankasolv", "stored");
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("po").feature("va1")
         .set("approxvanka", true);
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("po").feature("va1")
         .set("vankadirectmaxsize", 1000);
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("po").feature("va1").set("seconditer", 2);
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("po").feature("va1").set("relax", 0.5);
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("cs").label("Coarse Solver 1");
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("cs").feature("dDef").label("Direct 2");
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("cs").feature("d1").label("Direct 1.1");
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("cs").feature("d1")
         .set("linsolver", "pardiso");
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("cs").feature("d1")
         .set("pivotperturb", 1.0E-13);
    model.sol("sol1").feature("t1").feature("fc1").active(true);
    model.sol("sol1").feature("t1").feature("fc1").label("Fully Coupled 1.1");
    model.sol("sol1").feature("t1").feature("fc1").set("linsolver", "d2");
    model.sol("sol1").feature("t1").feature("fc1").set("jtech", "onevery");

    model.study("std1").runNoGen();

    model.sol("sol2").feature("st1").label("Compile Equations: Time Dependent");
    model.sol("sol2").feature("v1").label("Dependent Variables 1.1");
    model.sol("sol2").feature("v1").set("clist", new String[]{"{range(0, 0.5, 8.5)}[min]", "0.001[min]"});
    model.sol("sol2").feature("v1").feature("comp1_spatial_disp").set("scalemethod", "manual");
    model.sol("sol2").feature("v1").feature("comp1_spatial_disp").set("scaleval", 1.1906804777101203E-5);
    model.sol("sol2").feature("t1").label("Time-Dependent Solver 1.1");
    model.sol("sol2").feature("t1").set("tunit", "min");
    model.sol("sol2").feature("t1").set("tlist", "range(0,0.5,8.5)");
    model.sol("sol2").feature("t1").set("rtol", 0.005);
    model.sol("sol2").feature("t1").set("atolglobalfactor", 0.05);
    model.sol("sol2").feature("t1")
         .set("atolmethod", new String[]{"comp1_c", "global", "comp1_c_lm", "global", "comp1_nitf1_Uave", "global", "comp1_p", "scaled", "comp1_spatial_disp", "global", 
         "comp1_spatial_lm_nv", "global", "comp1_T", "global", "comp1_u", "global", "comp1_ODE1", "global"});
    model.sol("sol2").feature("t1")
         .set("atolfactor", new String[]{"comp1_c", "0.1", "comp1_c_lm", "0.1", "comp1_nitf1_Uave", "0.1", "comp1_p", "1", "comp1_spatial_disp", "0.1", 
         "comp1_spatial_lm_nv", "0.1", "comp1_T", "0.1", "comp1_u", "0.1", "comp1_ODE1", "0.1"});
    model.sol("sol2").feature("t1").set("initialstepbdfactive", true);
    model.sol("sol2").feature("t1").set("maxorder", 2);
    model.sol("sol2").feature("t1").set("stabcntrl", true);
    model.sol("sol2").feature("t1").set("bwinitstepfrac", 0.01);
    model.sol("sol2").feature("t1").set("estrat", "exclude");
    model.sol("sol2").feature("t1").feature("dDef").label("Direct 4");
    model.sol("sol2").feature("t1").feature("aDef").label("Advanced 1");
    model.sol("sol2").feature("t1").feature("aDef").set("cachepattern", true);
    model.sol("sol2").feature("t1").feature("se1").active(false);
    model.sol("sol2").feature("t1").feature("se1").label("Segregated 1.1");
    model.sol("sol2").feature("t1").feature("se1").set("ntolfact", 0.5);
    model.sol("sol2").feature("t1").feature("se1").set("segstabacc", "segaacc");
    model.sol("sol2").feature("t1").feature("se1").set("segaaccdim", 5);
    model.sol("sol2").feature("t1").feature("se1").set("segaaccmix", 0.9);
    model.sol("sol2").feature("t1").feature("se1").feature("ss1").label("Global ODEs and DAEs");
    model.sol("sol2").feature("t1").feature("se1").feature("ss1").set("segvar", new String[]{"comp1_ODE1"});
    model.sol("sol2").feature("t1").feature("se1").feature("ss1").set("subdamp", "0.7");
    model.sol("sol2").feature("t1").feature("se1").feature("ss1").set("subjtech", "onevery");
    model.sol("sol2").feature("t1").feature("se1").feature("ss2").label("Velocity u, Pressure p");
    model.sol("sol2").feature("t1").feature("se1").feature("ss2")
         .set("segvar", new String[]{"comp1_spatial_disp", "comp1_u", "comp1_p", "comp1_spatial_lm_nv"});
    model.sol("sol2").feature("t1").feature("se1").feature("ss2").set("linsolver", "d1");
    model.sol("sol2").feature("t1").feature("se1").feature("ss2").set("subdamp", "0.8");
    model.sol("sol2").feature("t1").feature("se1").feature("ss2").set("subjtech", "onevery");
    model.sol("sol2").feature("t1").feature("se1").feature("ss3").label("Temperature");
    model.sol("sol2").feature("t1").feature("se1").feature("ss3").set("segvar", new String[]{"comp1_T"});
    model.sol("sol2").feature("t1").feature("se1").feature("ss3").set("linsolver", "d2");
    model.sol("sol2").feature("t1").feature("se1").feature("ss3").set("subdamp", "0.7");
    model.sol("sol2").feature("t1").feature("se1").feature("ss3").set("subjtech", "onevery");
    model.sol("sol2").feature("t1").feature("se1").feature("ss4").label("Concentration c");
    model.sol("sol2").feature("t1").feature("se1").feature("ss4")
         .set("segvar", new String[]{"comp1_c", "comp1_c_lm"});
    model.sol("sol2").feature("t1").feature("se1").feature("ss4").set("linsolver", "d3");
    model.sol("sol2").feature("t1").feature("se1").feature("ss4").set("subdamp", "0.8");
    model.sol("sol2").feature("t1").feature("se1").feature("ss4").set("subjtech", "once");
    model.sol("sol2").feature("t1").feature("se1").feature("ll1").label("Lower Limit 1.1");
    model.sol("sol2").feature("t1").feature("se1").feature("ll1").set("lowerlimit", "comp1.T 0 ");
    model.sol("sol2").feature("t1").feature("d1").label("Direct, fluid flow variables (spf)");
    model.sol("sol2").feature("t1").feature("d1").set("linsolver", "pardiso");
    model.sol("sol2").feature("t1").feature("d1").set("pivotperturb", 1.0E-13);
    model.sol("sol2").feature("t1").feature("d2").label("Direct, heat transfer variables (ht)");
    model.sol("sol2").feature("t1").feature("d2").set("linsolver", "pardiso");
    model.sol("sol2").feature("t1").feature("d2").set("pivotperturb", 1.0E-13);
    model.sol("sol2").feature("t1").feature("d3").active(true);
    model.sol("sol2").feature("t1").feature("d3").label("Direct, concentrations (tds)");
    model.sol("sol2").feature("t1").feature("d3").set("linsolver", "pardiso");
    model.sol("sol2").feature("t1").feature("d3").set("pivotperturb", 1.0E-13);
    model.sol("sol2").feature("t1").feature("i1").label("Multiplicative Schwarz, fluid flow variables (spf)");
    model.sol("sol2").feature("t1").feature("i1").set("maxlinit", 100);
    model.sol("sol2").feature("t1").feature("i1").set("rhob", 20);
    model.sol("sol2").feature("t1").feature("i1").feature("ilDef").label("Incomplete LU 1");
    model.sol("sol2").feature("t1").feature("i1").feature("dd1").label("Domain Decomposition (Schwarz) 1.1");
    model.sol("sol2").feature("t1").feature("i1").feature("dd1").set("ndom", 1);
    model.sol("sol2").feature("t1").feature("i1").feature("dd1").set("overlap", 2);
    model.sol("sol2").feature("t1").feature("i1").feature("dd1").set("meshoverlap", false);
    model.sol("sol2").feature("t1").feature("i1").feature("dd1").set("ddolhandling", "ddrestricted");
    model.sol("sol2").feature("t1").feature("i1").feature("dd1").set("usecoarse", "aggregation");
    model.sol("sol2").feature("t1").feature("i1").feature("dd1").set("maxcoarsedof", 10000);
    model.sol("sol2").feature("t1").feature("i1").feature("dd1").set("maxcoarsedofactive", true);
    model.sol("sol2").feature("t1").feature("i1").feature("dd1").set("usesmooth", false);
    model.sol("sol2").feature("t1").feature("i1").feature("dd1").feature("cs").label("Coarse Solver 1");
    model.sol("sol2").feature("t1").feature("i1").feature("dd1").feature("cs").feature("dDef").label("Direct 2");
    model.sol("sol2").feature("t1").feature("i1").feature("dd1").feature("cs").feature("d1").label("Direct 1.1");
    model.sol("sol2").feature("t1").feature("i1").feature("dd1").feature("cs").feature("d1")
         .set("linsolver", "pardiso");
    model.sol("sol2").feature("t1").feature("i1").feature("dd1").feature("cs").feature("d1")
         .set("pivotperturb", 1.0E-13);
    model.sol("sol2").feature("t1").feature("i1").feature("dd1").feature("ds").label("Domain Solver 1");
    model.sol("sol2").feature("t1").feature("i1").feature("dd1").feature("ds").feature("dDef").label("Direct 2");
    model.sol("sol2").feature("t1").feature("i1").feature("dd1").feature("ds").feature("d1").label("Direct 1.1");
    model.sol("sol2").feature("t1").feature("i1").feature("dd1").feature("ds").feature("d1")
         .set("linsolver", "pardiso");
    model.sol("sol2").feature("t1").feature("i1").feature("dd1").feature("ds").feature("d1")
         .set("pivotperturb", 1.0E-13);
    model.sol("sol2").feature("t1").feature("i2").label("AMG, heat transfer variables (ht)");
    model.sol("sol2").feature("t1").feature("i2").set("rhob", 20);
    model.sol("sol2").feature("t1").feature("i2").feature("ilDef").label("Incomplete LU 1");
    model.sol("sol2").feature("t1").feature("i2").feature("mg1").label("Multigrid 1.1");
    model.sol("sol2").feature("t1").feature("i2").feature("mg1").set("prefun", "saamg");
    model.sol("sol2").feature("t1").feature("i2").feature("mg1").set("maxcoarsedof", 50000);
    model.sol("sol2").feature("t1").feature("i2").feature("mg1").set("nullspace", "constant");
    model.sol("sol2").feature("t1").feature("i2").feature("mg1").set("saamgcompwise", true);
    model.sol("sol2").feature("t1").feature("i2").feature("mg1").set("usesmooth", false);
    model.sol("sol2").feature("t1").feature("i2").feature("mg1").feature("pr").label("Presmoother 1");
    model.sol("sol2").feature("t1").feature("i2").feature("mg1").feature("pr").feature("soDef").label("SOR 2");
    model.sol("sol2").feature("t1").feature("i2").feature("mg1").feature("pr").feature("so1").label("SOR 1.1");
    model.sol("sol2").feature("t1").feature("i2").feature("mg1").feature("pr").feature("so1").set("relax", 0.9);
    model.sol("sol2").feature("t1").feature("i2").feature("mg1").feature("po").label("Postsmoother 1");
    model.sol("sol2").feature("t1").feature("i2").feature("mg1").feature("po").feature("soDef").label("SOR 2");
    model.sol("sol2").feature("t1").feature("i2").feature("mg1").feature("po").feature("so1").label("SOR 1.1");
    model.sol("sol2").feature("t1").feature("i2").feature("mg1").feature("po").feature("so1").set("relax", 0.9);
    model.sol("sol2").feature("t1").feature("i2").feature("mg1").feature("cs").label("Coarse Solver 1");
    model.sol("sol2").feature("t1").feature("i2").feature("mg1").feature("cs").feature("dDef").label("Direct 2");
    model.sol("sol2").feature("t1").feature("i2").feature("mg1").feature("cs").feature("d1").label("Direct 1.1");
    model.sol("sol2").feature("t1").feature("i2").feature("mg1").feature("cs").feature("d1")
         .set("linsolver", "pardiso");
    model.sol("sol2").feature("t1").feature("i2").feature("mg1").feature("cs").feature("d1")
         .set("pivotperturb", 1.0E-13);
    model.sol("sol2").feature("t1").feature("i3").label("AMG, concentrations (tds)");
    model.sol("sol2").feature("t1").feature("i3").set("maxlinit", 50);
    model.sol("sol2").feature("t1").feature("i3").feature("ilDef").label("Incomplete LU 1");
    model.sol("sol2").feature("t1").feature("i3").feature("mg1").label("Multigrid 1.1");
    model.sol("sol2").feature("t1").feature("i3").feature("mg1").set("prefun", "saamg");
    model.sol("sol2").feature("t1").feature("i3").feature("mg1").set("maxcoarsedof", 50000);
    model.sol("sol2").feature("t1").feature("i3").feature("mg1").set("nullspace", "constant");
    model.sol("sol2").feature("t1").feature("i3").feature("mg1").set("usesmooth", false);
    model.sol("sol2").feature("t1").feature("i3").feature("mg1").feature("pr").label("Presmoother 1");
    model.sol("sol2").feature("t1").feature("i3").feature("mg1").feature("pr").feature("soDef").label("SOR 1");
    model.sol("sol2").feature("t1").feature("i3").feature("mg1").feature("pr").feature("va1").label("Vanka 1.1");
    model.sol("sol2").feature("t1").feature("i3").feature("mg1").feature("pr").feature("va1")
         .set("linesweeptype", "ssor");
    model.sol("sol2").feature("t1").feature("i3").feature("mg1").feature("pr").feature("va1").set("iter", 1);
    model.sol("sol2").feature("t1").feature("i3").feature("mg1").feature("pr").feature("va1")
         .set("vankavars", new String[]{"comp1_c_lm"});
    model.sol("sol2").feature("t1").feature("i3").feature("mg1").feature("pr").feature("va1")
         .set("vankasolv", "stored");
    model.sol("sol2").feature("t1").feature("i3").feature("mg1").feature("pr").feature("va1")
         .set("approxvanka", true);
    model.sol("sol2").feature("t1").feature("i3").feature("mg1").feature("pr").feature("va1")
         .set("vankadirectmaxsize", 1000);
    model.sol("sol2").feature("t1").feature("i3").feature("mg1").feature("pr").feature("va1").set("relax", 0.5);
    model.sol("sol2").feature("t1").feature("i3").feature("mg1").feature("po").label("Postsmoother 1");
    model.sol("sol2").feature("t1").feature("i3").feature("mg1").feature("po").feature("soDef").label("SOR 1");
    model.sol("sol2").feature("t1").feature("i3").feature("mg1").feature("po").feature("va1").label("Vanka 1.1");
    model.sol("sol2").feature("t1").feature("i3").feature("mg1").feature("po").feature("va1")
         .set("linesweeptype", "ssor");
    model.sol("sol2").feature("t1").feature("i3").feature("mg1").feature("po").feature("va1").set("iter", 1);
    model.sol("sol2").feature("t1").feature("i3").feature("mg1").feature("po").feature("va1")
         .set("vankavars", new String[]{"comp1_c_lm"});

    return model;
  }

  public static Model run3(Model model) {
    model.sol("sol2").feature("t1").feature("i3").feature("mg1").feature("po").feature("va1")
         .set("vankasolv", "stored");
    model.sol("sol2").feature("t1").feature("i3").feature("mg1").feature("po").feature("va1")
         .set("approxvanka", true);
    model.sol("sol2").feature("t1").feature("i3").feature("mg1").feature("po").feature("va1")
         .set("vankadirectmaxsize", 1000);
    model.sol("sol2").feature("t1").feature("i3").feature("mg1").feature("po").feature("va1").set("seconditer", 2);
    model.sol("sol2").feature("t1").feature("i3").feature("mg1").feature("po").feature("va1").set("relax", 0.5);
    model.sol("sol2").feature("t1").feature("i3").feature("mg1").feature("cs").label("Coarse Solver 1");
    model.sol("sol2").feature("t1").feature("i3").feature("mg1").feature("cs").feature("dDef").label("Direct 2");
    model.sol("sol2").feature("t1").feature("i3").feature("mg1").feature("cs").feature("d1").label("Direct 1.1");
    model.sol("sol2").feature("t1").feature("i3").feature("mg1").feature("cs").feature("d1")
         .set("linsolver", "pardiso");
    model.sol("sol2").feature("t1").feature("i3").feature("mg1").feature("cs").feature("d1")
         .set("pivotperturb", 1.0E-13);
    model.sol("sol2").feature("t1").feature("fc1").active(true);
    model.sol("sol2").feature("t1").feature("fc1").label("Fully Coupled 1.1");
    model.sol("sol2").feature("t1").feature("fc1").set("linsolver", "d3");
    model.sol("sol2").feature("t1").feature("fc1").set("jtech", "onevery");

    model.study("std2").runNoGen();

    model.result().configuration("prfu1")
         .set("quantityunits", new String[][]{{"temperature", "Temperature", "K", "\u00b0C"}});
    model.result().dataset("rev1").label("Revolution 2D");
    model.result().dataset("rev1").set("startangle", -90);
    model.result().dataset("rev1").set("revangle", 225);
    model.result().dataset("dset3").label("Study 2 - Nonisothermal Case/Solution 2.1 (For Plotting)");
    model.result().dataset("rev2").label("Revolution 2D (For Plotting)");
    model.result("pg1").label("Isothermal Case");
    model.result("pg1").set("titletype", "custom");
    model.result("pg1").set("suffixintitle", "Verification - Isothermal Case");
    model.result("pg1").set("typeintitle", false);
    model.result("pg1").set("descriptionintitle", false);
    model.result("pg1").set("unitintitle", false);
    model.result("pg1").set("xlabel", "Time (min)");
    model.result("pg1").set("ylabel", "Droplet Volume (m<sup>3</sup>)");
    model.result("pg1").set("ylabelactive", true);
    model.result("pg1").set("axislimits", true);
    model.result("pg1").set("xmin", 0);
    model.result("pg1").set("xmax", 20);
    model.result("pg1").set("ymin", 0);
    model.result("pg1").set("ymax", "25e-10");
    model.result("pg1").set("manualgrid", true);
    model.result("pg1").set("xspacing", 4);
    model.result("pg1").set("yspacing", "5e-10");
    model.result("pg1").set("xlabelactive", false);
    model.result("pg1").feature("glob1").set("descr", new String[]{"Integration 1"});
    model.result("pg1").feature("glob1").set("linewidth", 2);
    model.result("pg1").feature("glob1").set("linewidthslider", 2);
    model.result("pg1").feature("glob1").set("legendmethod", "manual");
    model.result("pg1").feature("glob1").set("legends", new String[]{"COMSOL"});
    model.result("pg1").feature("glob2").set("linestyle", "dashed");
    model.result("pg1").feature("glob2").set("linewidth", 2);
    model.result("pg1").feature("glob2").set("linewidthslider", 2);
    model.result("pg1").feature("glob2").set("legendmethod", "manual");
    model.result("pg1").feature("glob2").set("legends", new String[]{"1D Analytical Solution"});
    model.result("pg9").label("Nonisothermal Case");
    model.result("pg9").set("titletype", "custom");
    model.result("pg9").set("suffixintitle", "Nonisothermal Case");
    model.result("pg9").set("typeintitle", false);
    model.result("pg9").set("descriptionintitle", false);
    model.result("pg9").set("unitintitle", false);
    model.result("pg9").set("xlabel", "Time (min)");
    model.result("pg9").set("ylabel", "Droplet Volume (m<sup>3</sup>)");
    model.result("pg9").set("ylabelactive", true);
    model.result("pg9").set("axislimits", true);
    model.result("pg9").set("xmin", 0);
    model.result("pg9").set("xmax", 20);
    model.result("pg9").set("ymin", 0);
    model.result("pg9").set("ymax", "25e-10");
    model.result("pg9").set("manualgrid", true);
    model.result("pg9").set("xspacing", 4);
    model.result("pg9").set("yspacing", "5e-10");
    model.result("pg9").set("xlabelactive", false);
    model.result("pg9").feature("glob1").set("descr", new String[]{"Integration 1"});
    model.result("pg9").feature("glob1").set("linewidth", 2);
    model.result("pg9").feature("glob1").set("linewidthslider", 2);
    model.result("pg9").feature("glob1").set("legendmethod", "manual");
    model.result("pg9").feature("glob1").set("legends", new String[]{"Nonisothermal, \\DELTA T=15 [K]"});
    model.result("pg9").feature("glob2").set("descr", new String[]{"Integration 1"});
    model.result("pg9").feature("glob2").set("linewidth", 2);
    model.result("pg9").feature("glob2").set("linewidthslider", 2);
    model.result("pg9").feature("glob2").set("legendmethod", "manual");
    model.result("pg9").feature("glob2").set("legends", new String[]{"Isothermal"});
    model.result("pg2").label("Velocity (spf)");
    model.result("pg2").set("looplevel", new int[]{1});
    model.result("pg2").set("frametype", "spatial");
    model.result("pg2").feature("surf1").label("Surface");
    model.result("pg2").feature("surf1").set("colortable", "RainbowClassic");
    model.result("pg2").feature("surf1").set("smooth", "internal");
    model.result("pg2").feature("surf1").set("resolution", "normal");
    model.result("pg5").label("Concentration (tds)");
    model.result("pg5").set("looplevel", new int[]{1});
    model.result("pg5").set("titletype", "custom");
    model.result("pg5").feature("surf1").set("colortable", "RainbowClassic");
    model.result("pg5").feature("surf1").set("resolution", "normal");
    model.result("pg5").feature("str1").set("posmethod", "uniform");
    model.result("pg5").feature("str1").set("pointtype", "arrow");
    model.result("pg5").feature("str1").set("arrowcount", 24);
    model.result("pg5").feature("str1").set("arrowlength", "logarithmic");
    model.result("pg5").feature("str1").set("arrowscale", 1.8981009052084758E20);
    model.result("pg5").feature("str1").set("color", "gray");
    model.result("pg5").feature("str1").set("recover", "pprint");
    model.result("pg5").feature("str1").set("arrowcountactive", false);
    model.result("pg5").feature("str1").set("arrowscaleactive", false);
    model.result("pg5").feature("str1").set("resolution", "normal");
    model.result("pg8").label("Temperature (ht)");
    model.result("pg8").set("looplevel", new int[]{1});
    model.result("pg8").feature("surf1").set("unit", "\u00b0C");
    model.result("pg8").feature("surf1").set("colortable", "HeatCameraLight");
    model.result("pg8").feature("surf1").set("resolution", "normal");
    model.result("pg11").label("3D Temperature Profile");
    model.result("pg11").set("looplevel", new String[]{"last"});
    model.result("pg11").set("edges", false);
    model.result("pg11").feature("surf1").set("unit", "\u00b0C");
    model.result("pg11").feature("surf1").set("colortable", "HeatCameraLight");
    model.result("pg11").feature("surf1").set("resolution", "normal");

    model.nodeGroup("grp1").label("Nonisothermal Case");
    model.nodeGroup("grp1").add("plotgroup", "pg9");
    model.nodeGroup("grp1").add("plotgroup", "pg2");
    model.nodeGroup("grp1").add("plotgroup", "pg5");
    model.nodeGroup("grp1").add("plotgroup", "pg8");
    model.nodeGroup("grp1").add("plotgroup", "pg11");

    return model;
  }

  public static void main(String[] args) {
    Model model = run();
    model = run2(model);
    run3(model);
  }

}
