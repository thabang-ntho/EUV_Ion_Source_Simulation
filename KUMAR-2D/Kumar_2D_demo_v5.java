/*
 * Kumar_2D_demo_v5.java
 */

import com.comsol.model.*;
import com.comsol.model.util.*;

/** Model exported on Aug 19 2025, 09:24 by COMSOL 6.2.0.290. */
public class Kumar_2D_demo_v5 {

  public static Model run() {
    Model model = ModelUtil.create("Model");

    model.modelPath("/home/xdadmin/Documents/Vital-WORK/2025/EUV_Lithography/OLD_STUFF_TO_DELETE/KUMAR-2D");

    model.label("Kumar_2D_demo_v5.mph");

    model.param().set("a_abs", "0.30", "Absorptivity of molten Sn at 1064 nm");
    model.param().set("beta_r", "0.15", "Recombination coefficient");
    model.param().set("Cp_sn", "237[J/(kg*K)]", "Heat capacity of Sn");
    model.param().set("d_beam", "20[um]", "Beam FWHM diameter");
    model.param().set("d_sigma_dT", "-1.6e-4[N/(m*K)]", "d\u03c3/dT (Marangoni coefficient)");
    model.param().set("Dm0", "1e-3[m^2/s]", "Fuller base diffusivity");
    model.param().set("dXY_ref", "1e-7[m]", "Reference displacement (100 nm)        << NEW");
    model.param().set("dXY_smooth", "0.5", "Smoothing half-width  (\u00d7 dXY_ref)      << updated");
    model.param().set("dXY_thresh", "1", "Displacement threshold (\u00d7 dXY_ref)     << updated");
    model.param().set("eps_dXY", "1e-5", "Regularisation term for dXY  (unit-less)");
    model.param().set("E_pulse", "8e-4[J]", "Pulse energy (0.8 mJ)");
    model.param().set("Ed", "E_pulse/((pi/4)*d_beam^2)", "Fluence (auto)");
    model.param().set("Ed_rate", "Ed/t_pulse", "Average power density during pulse");
    model.param().set("eps_t", "1e-10[s]", "Smoothing width for 10 ns gate");
    model.param().set("G_sigma", "d_beam/sqrt(8*log(2))", "Gaussian \u03c3 from FWHM");
    model.param().set("H_dom", "300[um]", "Box height");
    model.param().set("k_sn", "31[W/(m*K)]", "Thermal conductivity of Sn");
    model.param().set("Lf_sn", "5.9e4[J/kg]", "Latent heat of fusion");
    model.param().set("Lv_mol", "Lv_sn*M_sn", "Molar latent heat of Sn");
    model.param().set("Lv_sn", "2.96e6[J/kg]", "Latent heat of vaporisation");
    model.param().set("M_sn", "118.71e-3[kg/mol]", "Molar mass of Sn");
    model.param().set("mesh_size_ext", "5[um]", "Base mesh size in gas");
    model.param().set("mesh_size_int", "1[um]", "Base mesh size inside droplet");
    model.param().set("mu_sn", "1.8e-3[Pa*s]", "Dynamic viscosity of molten Sn");
    model.param().set("Mw_H2", "2.016e-3[kg/mol]", "Molar mass of H\u2082");
    model.param().set("P_amb", "1.333[Pa]", "Background pressure (10 mTorr)");
    model.param().set("P_laser", "E_pulse/t_pulse", "Peak laser power (auto)");
    model.param().set("P_ref", "1[atm]", "Reference pressure for Psat(T)");
    model.param().set("R_drop", "15[um]", "Tin droplet radius");
    model.param().set("rho_sn", "6980[kg/m^3]", "Density of Sn");
    model.param().set("Rl_spot", "d_beam/2", "1/e\u00b2 beam radius");
    model.param().set("sconst", "1e6", "Mesh stiffening magnitude (unit-less)  << updated");
    model.param().set("sigma_f", "0.556[N/m]", "Surface tension at T_melt");
    model.param().set("T_amb", "300[K]", "Background temperature");
    model.param().set("t_pulse", "10[ns]", "Pulse duration");
    model.param().set("t_start", "0[s]", "Pulse start time");
    model.param().set("t_step", "1[ns]", "Nominal solver time step");
    model.param().set("Tboil_sn", "2875[K]", "Boiling temperature of Sn");
    model.param().set("Tmelt_sn", "778[K]", "Melting temperature of Sn");
    model.param().set("W_dom", "200[um]", "Box half-width");
    model.param().set("x0", "W_dom/2", "Droplet centre x-coordinate");
    model.param().set("y0", "H_dom/2", "Droplet centre y-coordinate");

    model.component().create("comp1", true);

    model.component("comp1").geom().create("geom1", 2);

    model.result().table().create("tbl1", "Table");

    model.component("comp1").func().create("step1", "Step");
    model.component("comp1").func().create("an1", "Analytic");
    model.component("comp1").func().create("an4", "Analytic");
    model.component("comp1").func("step1").set("funcname", "pulse");
    model.component("comp1").func("step1").set("from", "t_start");
    model.component("comp1").func("step1").set("to", "t_start + t_pulse");
    model.component("comp1").func("step1").set("smooth", "eps_t");
    model.component("comp1").func("an1").label("Analytical 1");
    model.component("comp1").func("an1").set("funcname", "gaussXY");
    model.component("comp1").func("an1").set("expr", "exp(-((x-x0)^2 + (y-y0)^2)/(2*G_sigma^2))");
    model.component("comp1").func("an1").set("args", new String[]{"x", "y"});
    model.component("comp1").func("an1").set("argunit", new String[]{"m", "m"});
    model.component("comp1").func("an1").set("plotaxis", new String[]{"on", "on"});
    model.component("comp1").func("an1").set("plotfixedvalue", new String[]{"0", "0"});
    model.component("comp1").func("an1").set("plotargs", new String[][]{{"x", "0", "1"}, {"y", "0", "1"}});
    model.component("comp1").func("an4").set("funcname", "sigma");
    model.component("comp1").func("an4").set("expr", "sigma_f + d_sigma_dT*(T - Tmelt_sn)");
    model.component("comp1").func("an4").set("args", new String[]{"T"});
    model.component("comp1").func("an4").set("argunit", new String[]{""});
    model.component("comp1").func("an4").set("plotargs", new String[][]{{"T", "0", "1"}});

    model.component("comp1").mesh().create("mesh1");

    model.component("comp1").geom("geom1").lengthUnit("\u00b5m");
    model.component("comp1").geom("geom1").create("r1", "Rectangle");
    model.component("comp1").geom("geom1").feature("r1").label("Rectangle 1 vac_box");
    model.component("comp1").geom("geom1").feature("r1").set("size", new String[]{"W_dom", "H_dom"});
    model.component("comp1").geom("geom1").create("c1", "Circle");
    model.component("comp1").geom("geom1").feature("c1").label("Circle 1  droplet");
    model.component("comp1").geom("geom1").feature("c1").set("pos", new String[]{"W_dom/2", "H_dom/2"});
    model.component("comp1").geom("geom1").feature("c1").set("r", "R_drop");
    model.component("comp1").geom("geom1").run();
    model.component("comp1").geom("geom1").run("fin");

    model.component("comp1").variable().create("var1");
    model.component("comp1").variable("var1").set("J_evap", "(1-beta_r)*Psat*sqrt(M_sn/(2*pi*R_const*T))");
    model.component("comp1").variable("var1").selection().geom("geom1", 1);
    model.component("comp1").variable("var1").selection().set(5, 6, 7, 8);
    model.component("comp1").variable().create("var2");
    model.component("comp1").variable("var2").set("Psat", "P_ref*exp( Lv_mol/R_const*(1/Tboil_sn - 1/T) )");
    model.component("comp1").variable("var2").selection().geom("geom1", 1);
    model.component("comp1").variable("var2").selection().set(5, 6, 7, 8);
    model.component("comp1").variable().create("var3");
    model.component("comp1").variable("var3")
         .set("q_laser", "(2*a_abs*P_laser)/(pi*Rl_spot^2)*exp(-2*((x - x0)^2 + (y - y0)^2)/Rl_spot^2)*pulse(t)/1[s]", "Laser heat source");
    model.component("comp1").variable("var3").selection().geom("geom1", 1);
    model.component("comp1").variable("var3").selection().set(5, 6, 7, 8);
    model.component("comp1").variable().create("var4");
    model.component("comp1").variable("var4")
         .set("phi_m", "c*(R_const*T)/(nitf2.pA)", "Local molar fraction of Sn atoms");
    model.component("comp1").variable().create("var5");
    model.component("comp1").variable("var5")
         .set("S", "sconst * flc2hs(dXY - dXY_thresh , dXY_smooth)", "stiffness factor (Eq. 31)");
    model.component("comp1").variable("var5").selection().geom("geom1", 2);
    model.component("comp1").variable("var5").selection().set(2);
    model.component("comp1").variable().create("var6");
    model.component("comp1").variable("var6").set("dXY", "sqrt(material.u^2 + material.v^2 + eps_dXY^2) / dXY_ref");
    model.component("comp1").variable("var6").selection().geom("geom1", 2);
    model.component("comp1").variable("var6").selection().set(2);
    model.component("comp1").variable().create("var7");
    model.component("comp1").variable("var7").set("v_n", "J_evap / rho_sn", "Normal velocity due to evaporation");

    model.component("comp1").material().create("mat1", "Common");
    model.component("comp1").material().create("mat2", "Common");
    model.component("comp1").material("mat1").selection().set(1);
    model.component("comp1").material("mat1").propertyGroup("def").func().create("int1", "Interpolation");
    model.component("comp1").material("mat1").propertyGroup("def").func().create("int2", "Interpolation");
    model.component("comp1").material("mat1").propertyGroup("def").func().create("int3", "Interpolation");
    model.component("comp1").material("mat1").propertyGroup("def").func().create("int4", "Interpolation");
    model.component("comp1").material("mat1").propertyGroup("def").func().create("int5", "Interpolation");
    model.component("comp1").material("mat1").propertyGroup()
         .create("RadiationHeatTransfer", "Radiation heat transfer");
    model.component("comp1").material("mat1").propertyGroup("RadiationHeatTransfer").func()
         .create("int1", "Interpolation");
    model.component("comp1").material("mat2").selection().set(2);
    model.component("comp1").material("mat2").info().create("UNS");
    model.component("comp1").material("mat2").propertyGroup("def").func().create("k_liquid_2", "Piecewise");
    model.component("comp1").material("mat2").propertyGroup("def").func().create("res_liquid_2", "Piecewise");
    model.component("comp1").material("mat2").propertyGroup("def").func().create("alpha_liquid_4", "Piecewise");
    model.component("comp1").material("mat2").propertyGroup("def").func().create("C_liquid_2", "Piecewise");
    model.component("comp1").material("mat2").propertyGroup("def").func().create("sigma_liquid_2", "Piecewise");
    model.component("comp1").material("mat2").propertyGroup("def").func().create("HC_liquid_2", "Piecewise");
    model.component("comp1").material("mat2").propertyGroup("def").func().create("VP_liquid_2", "Piecewise");
    model.component("comp1").material("mat2").propertyGroup("def").func().create("rho_liquid_2", "Piecewise");
    model.component("comp1").material("mat2").propertyGroup("def").func().create("TD_liquid_2", "Piecewise");
    model.component("comp1").material("mat2").propertyGroup("def").func().create("eta", "Piecewise");
    model.component("comp1").material("mat2").propertyGroup("def").func().create("app_eta", "Piecewise");
    model.component("comp1").material("mat2").propertyGroup("def").func().create("SurfF", "Piecewise");
    model.component("comp1").material("mat2").propertyGroup().create("ThermalExpansion", "Thermal expansion");
    model.component("comp1").material("mat2").propertyGroup("ThermalExpansion").func()
         .create("dL_liquid_4", "Piecewise");

    model.component("comp1").common().create("free1", "DeformingDomainDeformedGeometry");
    model.component("comp1").common().create("disp2", "PrescribedMeshVelocityDeformedGeometry");
    model.component("comp1").common().create("free2", "DeformingDomainDeformedGeometry");
    model.component("comp1").common().create("fix1", "FixedBoundaryDeformedGeometry");
    model.component("comp1").common("free1").selection().set(2);
    model.component("comp1").common("disp2").selection().set(5, 6, 7, 8);
    model.component("comp1").common("free2").selection().set(1);
    model.component("comp1").common("fix1").selection().set(1, 2, 3, 4);

    model.component("comp1").physics().create("ht", "HeatTransferInFluids", "geom1");
    model.component("comp1").physics("ht").selection().set(2);
    model.component("comp1").physics("ht").create("bhs1", "BoundaryHeatSource", 1);
    model.component("comp1").physics("ht").feature("bhs1").selection().set(5, 6, 7, 8);
    model.component("comp1").physics().create("ht2", "HeatTransferInFluids", "geom1");
    model.component("comp1").physics("ht2").selection().set(1);
    model.component("comp1").physics("ht2").create("bhs1", "BoundaryHeatSource", 1);
    model.component("comp1").physics("ht2").feature("bhs1").selection().set(5, 6, 7, 8);
    model.component("comp1").physics().create("spf", "LaminarFlow", "geom1");
    model.component("comp1").physics("spf").selection().set(2);
    model.component("comp1").physics("spf").create("bs1", "BoundaryStress", 1);
    model.component("comp1").physics("spf").feature("bs1").selection().set(5, 6, 7, 8);
    model.component("comp1").physics().create("spf2", "LaminarFlow", "geom1");
    model.component("comp1").physics("spf2").selection().set(1);
    model.component("comp1").physics("spf2").create("bs1", "BoundaryStress", 1);
    model.component("comp1").physics("spf2").feature("bs1").selection().set(5, 6, 7, 8);
    model.component("comp1").physics().create("tds", "DilutedSpecies", "geom1");
    model.component("comp1").physics("tds").selection().set(1);
    model.component("comp1").physics("tds").create("fl1", "FluxBoundary", 1);
    model.component("comp1").physics("tds").feature("fl1").selection().set(5, 6, 7, 8);
    model.component("comp1").physics("tds").create("cdm2", "ConvectionDiffusionMigration", 2);
    model.component("comp1").physics("tds").feature("cdm2").selection().set(1);

    model.component("comp1").multiphysics().create("nitf1", "NonIsothermalFlow", 2);
    model.component("comp1").multiphysics().create("nitf2", "NonIsothermalFlow", 2);

    model.component("comp1").mesh("mesh1").create("ftri2", "FreeTri");
    model.component("comp1").mesh("mesh1").create("ftri3", "FreeTri");
    model.component("comp1").mesh("mesh1").feature("ftri2").selection().geom("geom1", 2);
    model.component("comp1").mesh("mesh1").feature("ftri2").selection().set(2);
    model.component("comp1").mesh("mesh1").feature("ftri2").create("size1", "Size");
    model.component("comp1").mesh("mesh1").feature("ftri3").selection().geom("geom1", 2);
    model.component("comp1").mesh("mesh1").feature("ftri3").selection().set(1);
    model.component("comp1").mesh("mesh1").feature("ftri3").create("size1", "Size");

    model.component("comp1").probe().create("dom1", "Domain");
    model.component("comp1").probe("dom1").selection().set(2);

    model.result().table("tbl1").label("Probe Table 1");

    model.component("comp1").variable("var1").label("Variable 1 Hertz-Knudsen mass flux for evaporation");
    model.component("comp1").variable("var2").label("Variables 2 Psat");
    model.component("comp1").variable("var3").label("Variables 3 q_laser");
    model.component("comp1").variable("var4").label("Variable 4 Local molar fraction of Sn atoms ");
    model.component("comp1").variable("var5").label("Variables 5 Mesh stiffness  S");
    model.component("comp1").variable("var6").label("Variables 6 Total mesh displacment dXY");
    model.component("comp1").variable("var7").label("Variables 7   Evaporation-driven normal velocity");

    model.component("comp1").view("view1").axis().set("xmin", -58.979278564453125);
    model.component("comp1").view("view1").axis().set("xmax", 258.9792785644531);
    model.component("comp1").view("view1").axis().set("ymin", -14.999968528747559);
    model.component("comp1").view("view1").axis().set("ymax", 315);

    model.component("comp1").material("mat1").label("Hydrogen");
    model.component("comp1").material("mat1").propertyGroup("def").func("int1").set("funcname", "rho");
    model.component("comp1").material("mat1").propertyGroup("def").func("int1")
         .set("table", new String[][]{{"5.0000E+02", "4.8646E-02"}, 
         {"6.0000E+02", "4.0509E-02"}, 
         {"7.0000E+02", "3.4703E-02"}, 
         {"8.0000E+02", "3.0353E-02"}, 
         {"9.0000E+02", "2.6971E-02"}, 
         {"1.0000E+03", "2.4267E-02"}, 
         {"1.1000E+03", "2.2056E-02"}, 
         {"1.2000E+03", "2.0214E-02"}, 
         {"1.3000E+03", "1.8656E-02"}, 
         {"1.4000E+03", "1.7321E-02"}, 
         {"1.5000E+03", "1.6164E-02"}, 
         {"1.6000E+03", "1.5152E-02"}, 
         {"1.7000E+03", "1.4259E-02"}, 
         {"1.8000E+03", "1.3464E-02"}, 
         {"1.9000E+03", "1.2752E-02"}, 
         {"2.0000E+03", "1.2109E-02"}, 
         {"2.1000E+03", "1.1523E-02"}, 
         {"2.2000E+03", "1.0986E-02"}, 
         {"2.3000E+03", "1.0488E-02"}, 
         {"2.4000E+03", "1.0022E-02"}, 
         {"2.5000E+03", "9.5792E-03"}, 
         {"2.6000E+03", "9.1543E-03"}, 
         {"2.7000E+03", "8.7407E-03"}, 
         {"2.8000E+03", "8.3331E-03"}, 
         {"2.9000E+03", "7.9270E-03"}, 
         {"3.0000E+03", "7.5189E-03"}, 
         {"3.1000E+03", "7.1071E-03"}, 
         {"3.2000E+03", "6.6914E-03"}, 
         {"3.3000E+03", "6.2740E-03"}, 
         {"3.4000E+03", "5.8588E-03"}, 
         {"3.5000E+03", "5.4520E-03"}, 
         {"3.6000E+03", "5.0607E-03"}, 
         {"3.7000E+03", "4.6924E-03"}, 
         {"3.8000E+03", "4.3540E-03"}, 
         {"3.9000E+03", "4.0502E-03"}, 
         {"4.0000E+03", "3.7833E-03"}, 
         {"4.1000E+03", "3.5529E-03"}, 
         {"4.2000E+03", "3.3562E-03"}, 
         {"4.3000E+03", "3.1893E-03"}, 
         {"4.4000E+03", "3.0477E-03"}, 
         {"4.5000E+03", "2.9267E-03"}, 
         {"4.6000E+03", "2.8224E-03"}, 
         {"4.7000E+03", "2.7313E-03"}, 
         {"4.8000E+03", "2.6508E-03"}, 
         {"4.9000E+03", "2.5788E-03"}, 
         {"5.0000E+03", "2.5135E-03"}, 
         {"5.1000E+03", "2.4536E-03"}, 
         {"5.2000E+03", "2.3983E-03"}, 
         {"5.3000E+03", "2.3467E-03"}, 
         {"5.4000E+03", "2.2982E-03"}, 
         {"5.5000E+03", "2.2525E-03"}, 
         {"5.6000E+03", "2.2092E-03"}, 
         {"5.7000E+03", "2.1680E-03"}, 
         {"5.8000E+03", "2.1286E-03"}, 
         {"5.9000E+03", "2.0909E-03"}, 
         {"6.0000E+03", "2.0547E-03"}, 
         {"6.1000E+03", "2.0200E-03"}, 
         {"6.2000E+03", "1.9865E-03"}, 
         {"6.3000E+03", "1.9542E-03"}, 
         {"6.4000E+03", "1.9230E-03"}, 
         {"6.5000E+03", "1.8929E-03"}, 
         {"6.6000E+03", "1.8637E-03"}, 
         {"6.7000E+03", "1.8355E-03"}, 
         {"6.8000E+03", "1.8081E-03"}, 
         {"6.9000E+03", "1.7815E-03"}, 
         {"7.0000E+03", "1.7557E-03"}, 
         {"7.1000E+03", "1.7306E-03"}, 
         {"7.2000E+03", "1.7063E-03"}, 
         {"7.3000E+03", "1.6826E-03"}, 
         {"7.4000E+03", "1.6595E-03"}, 
         {"7.5000E+03", "1.6370E-03"}, 
         {"7.6000E+03", "1.6151E-03"}, 
         {"7.7000E+03", "1.5937E-03"}, 
         {"7.8000E+03", "1.5728E-03"}, 
         {"7.9000E+03", "1.5524E-03"}, 
         {"8.0000E+03", "1.5325E-03"}, 
         {"8.1000E+03", "1.5131E-03"}, 
         {"8.2000E+03", "1.4940E-03"}, 
         {"8.3000E+03", "1.4754E-03"}, 
         {"8.4000E+03", "1.4511E-03"}, 
         {"8.5000E+03", "1.4392E-03"}, 
         {"8.6000E+03", "1.4216E-03"}, 
         {"8.7000E+03", "1.4044E-03"}, 
         {"8.8000E+03", "1.3874E-03"}, 
         {"8.9000E+03", "1.3708E-03"}, 
         {"9.0000E+03", "1.3544E-03"}, 
         {"9.1000E+03", "1.3383E-03"}, 
         {"9.2000E+03", "1.3224E-03"}, 
         {"9.3000E+03", "1.3068E-03"}, 
         {"9.4000E+03", "1.2913E-03"}, 
         {"9.5000E+03", "1.2761E-03"}, 
         {"9.6000E+03", "1.2610E-03"}, 
         {"9.7000E+03", "1.2462E-03"}, 
         {"9.8000E+03", "1.2315E-03"}, 
         {"9.9000E+03", "1.2169E-03"}, 
         {"1.0000E+04", "1.2025E-03"}, 
         {"1.0100E+04", "1.1882E-03"}, 
         {"1.0200E+04", "1.1740E-03"}, 
         {"1.0300E+04", "1.1599E-03"}, 
         {"1.0400E+04", "1.1459E-03"}, 
         {"1.0500E+04", "1.1321E-03"}, 
         {"1.0600E+04", "1.1182E-03"}, 
         {"1.0700E+04", "1.1045E-03"}, 
         {"1.0800E+04", "1.0908E-03"}, 
         {"1.0900E+04", "1.0772E-03"}, 
         {"1.1000E+04", "1.0637E-03"}, 
         {"1.1100E+04", "1.0501E-03"}, 
         {"1.1200E+04", "1.0367E-03"}, 
         {"1.1300E+04", "1.0232E-03"}, 
         {"1.1400E+04", "1.0098E-03"}, 
         {"1.1500E+04", "9.9643E-04"}, 
         {"1.1600E+04", "9.8308E-04"}, 
         {"1.1700E+04", "9.6975E-04"}, 
         {"1.1800E+04", "9.5643E-04"}, 
         {"1.1900E+04", "9.4315E-04"}, 
         {"1.2000E+04", "9.2990E-04"}, 
         {"1.2100E+04", "9.1666E-04"}, 
         {"1.2200E+04", "9.0346E-04"}, 
         {"1.2300E+04", "8.9028E-04"}, 
         {"1.2400E+04", "8.7710E-04"}, 
         {"1.2500E+04", "8.6399E-04"}, 
         {"1.2600E+04", "8.5092E-04"}, 
         {"1.2700E+04", "8.3789E-04"}, 
         {"1.2800E+04", "8.2491E-04"}, 
         {"1.2900E+04", "8.1198E-04"}, 
         {"1.3000E+04", "7.9913E-04"}, 
         {"1.3100E+04", "7.8634E-04"}, 
         {"1.3200E+04", "7.7363E-04"}, 
         {"1.3300E+04", "7.6092E-04"}, 
         {"1.3400E+04", "7.4839E-04"}, 
         {"1.3500E+04", "7.3595E-04"}, 
         {"1.3600E+04", "7.2364E-04"}, 
         {"1.3700E+04", "7.1144E-04"}, 
         {"1.3800E+04", "6.9937E-04"}, 
         {"1.3900E+04", "6.8745E-04"}, 
         {"1.4000E+04", "6.7568E-04"}, 
         {"1.4100E+04", "6.6406E-04"}, 
         {"1.4200E+04", "6.5262E-04"}, 
         {"1.4300E+04", "6.4135E-04"}, 
         {"1.4400E+04", "6.3028E-04"}, 
         {"1.4500E+04", "6.1939E-04"}, 
         {"1.4600E+04", "6.0872E-04"}, 
         {"1.4700E+04", "5.9825E-04"}, 
         {"1.4800E+04", "5.8799E-04"}, 
         {"1.4900E+04", "5.7797E-04"}, 
         {"1.5000E+04", "5.6788E-04"}, 
         {"1.5100E+04", "5.5830E-04"}, 
         {"1.5200E+04", "5.4895E-04"}, 
         {"1.5300E+04", "5.3984E-04"}, 
         {"1.5400E+04", "5.3097E-04"}, 
         {"1.5500E+04", "5.2235E-04"}, 
         {"1.5600E+04", "5.1397E-04"}, 
         {"1.5700E+04", "5.0583E-04"}, 
         {"1.5800E+04", "4.9793E-04"}, 
         {"1.5900E+04", "4.9028E-04"}, 
         {"1.6000E+04", "4.8286E-04"}, 
         {"1.6100E+04", "4.7568E-04"}, 
         {"1.6200E+04", "4.6874E-04"}, 
         {"1.6300E+04", "4.6202E-04"}, 
         {"1.6400E+04", "4.5552E-04"}, 
         {"1.6500E+04", "4.4924E-04"}, 
         {"1.6600E+04", "4.4318E-04"}, 
         {"1.6700E+04", "4.3732E-04"}, 
         {"1.6800E+04", "4.3167E-04"}, 
         {"1.6900E+04", "4.2621E-04"}, 
         {"1.7000E+04", "4.2094E-04"}, 
         {"1.7100E+04", "4.1585E-04"}, 
         {"1.7200E+04", "4.1094E-04"}, 
         {"1.7300E+04", "4.0620E-04"}, 
         {"1.7400E+04", "4.0162E-04"}, 
         {"1.7500E+04", "3.9720E-04"}, 
         {"1.7600E+04", "3.9293E-04"}, 
         {"1.7700E+04", "3.8881E-04"}, 
         {"1.7800E+04", "3.8482E-04"}, 
         {"1.7900E+04", "3.8096E-04"}, 
         {"1.8000E+04", "3.7723E-04"}, 
         {"1.8100E+04", "3.7362E-04"}, 
         {"1.8200E+04", "3.7070E-04"}, 
         {"1.8300E+04", "3.6731E-04"}, 
         {"1.8400E+04", "3.6403E-04"}, 
         {"1.8500E+04", "3.6084E-04"}, 
         {"1.8600E+04", "3.5775E-04"}, 
         {"1.8700E+04", "3.5475E-04"}, 
         {"1.8800E+04", "3.5184E-04"}, 
         {"1.8900E+04", "3.4901E-04"}, 
         {"1.9000E+04", "3.4625E-04"}, 
         {"1.9100E+04", "3.4357E-04"}, 
         {"1.9200E+04", "3.4096E-04"}, 
         {"1.9300E+04", "3.3842E-04"}, 
         {"1.9400E+04", "3.3595E-04"}, 
         {"1.9500E+04", "3.3353E-04"}, 
         {"1.9600E+04", "3.3117E-04"}, 
         {"1.9700E+04", "3.2887E-04"}, 
         {"1.9800E+04", "3.2662E-04"}, 
         {"1.9900E+04", "3.2442E-04"}, 
         {"2.0000E+04", "3.2227E-04"}, 
         {"2.0100E+04", "3.2017E-04"}, 
         {"2.0200E+04", "3.1811E-04"}, 
         {"2.0300E+04", "3.1610E-04"}, 
         {"2.0400E+04", "3.1412E-04"}, 
         {"2.0500E+04", "3.1218E-04"}, 
         {"2.0600E+04", "3.1029E-04"}, 
         {"2.0700E+04", "3.0842E-04"}, 
         {"2.0800E+04", "3.0659E-04"}, 
         {"2.0900E+04", "3.0480E-04"}, 
         {"2.1000E+04", "3.0303E-04"}, 
         {"2.1100E+04", "3.0130E-04"}, 
         {"2.1200E+04", "2.9960E-04"}, 
         {"2.1300E+04", "2.9792E-04"}, 
         {"2.1400E+04", "2.9627E-04"}, 
         {"2.1500E+04", "2.9465E-04"}, 
         {"2.1600E+04", "2.9305E-04"}, 
         {"2.1700E+04", "2.9148E-04"}, 
         {"2.1800E+04", "2.8993E-04"}, 
         {"2.1900E+04", "2.8841E-04"}, 
         {"2.2000E+04", "2.8690E-04"}, 
         {"2.2100E+04", "2.8587E-04"}, 
         {"2.2200E+04", "2.8440E-04"}, 
         {"2.2300E+04", "2.8296E-04"}, 
         {"2.2400E+04", "2.8153E-04"}, 
         {"2.2500E+04", "2.8012E-04"}, 
         {"2.2600E+04", "2.7873E-04"}, 
         {"2.2700E+04", "2.7735E-04"}, 
         {"2.2800E+04", "2.7600E-04"}, 
         {"2.2900E+04", "2.7466E-04"}, 
         {"2.3000E+04", "2.7334E-04"}, 
         {"2.3100E+04", "2.7203E-04"}, 
         {"2.3200E+04", "2.7074E-04"}, 
         {"2.3300E+04", "2.6946E-04"}, 
         {"2.3400E+04", "2.6820E-04"}, 
         {"2.3500E+04", "2.6696E-04"}, 
         {"2.3600E+04", "2.6572E-04"}, 
         {"2.3700E+04", "2.6451E-04"}, 
         {"2.3800E+04", "2.6330E-04"}, 
         {"2.3900E+04", "2.6211E-04"}, 
         {"2.4000E+04", "2.6093E-04"}});
    model.component("comp1").material("mat1").propertyGroup("def").func("int1").set("interp", "piecewisecubic");
    model.component("comp1").material("mat1").propertyGroup("def").func("int1").set("extrap", "linear");
    model.component("comp1").material("mat1").propertyGroup("def").func("int1")
         .set("fununit", new String[]{"kg/m^3"});
    model.component("comp1").material("mat1").propertyGroup("def").func("int1").set("argunit", new String[]{"K"});
    model.component("comp1").material("mat1").propertyGroup("def").func("int2").set("funcname", "cp");
    model.component("comp1").material("mat1").propertyGroup("def").func("int2")
         .set("table", new String[][]{{"5.0000E+02", "1.4450E+04"}, 
         {"6.0000E+02", "1.5039E+04"}, 
         {"7.0000E+02", "1.5289E+04"}, 
         {"8.0000E+02", "1.5552E+04"}, 
         {"9.0000E+02", "1.5824E+04"}, 
         {"1.0000E+03", "1.6105E+04"}, 
         {"1.1000E+03", "1.6393E+04"}, 
         {"1.2000E+03", "1.6686E+04"}, 
         {"1.3000E+03", "1.6984E+04"}, 
         {"1.4000E+03", "1.7286E+04"}, 
         {"1.5000E+03", "1.7597E+04"}, 
         {"1.6000E+03", "1.7924E+04"}, 
         {"1.7000E+03", "1.8285E+04"}, 
         {"1.8000E+03", "1.8711E+04"}, 
         {"1.9000E+03", "1.9251E+04"}, 
         {"2.0000E+03", "1.9972E+04"}, 
         {"2.1000E+03", "2.0968E+04"}, 
         {"2.2000E+03", "2.2354E+04"}, 
         {"2.3000E+03", "2.4269E+04"}, 
         {"2.4000E+03", "2.6870E+04"}, 
         {"2.5000E+03", "3.0329E+04"}, 
         {"2.6000E+03", "3.4832E+04"}, 
         {"2.7000E+03", "4.0564E+04"}, 
         {"2.8000E+03", "4.7710E+04"}, 
         {"2.9000E+03", "5.6441E+04"}, 
         {"3.0000E+03", "6.5895E+04"}, 
         {"3.1000E+03", "7.9148E+04"}, 
         {"3.2000E+03", "9.3162E+04"}, 
         {"3.3000E+03", "1.0871E+05"}, 
         {"3.4000E+03", "1.2528E+05"}, 
         {"3.5000E+03", "1.4196E+05"}, 
         {"3.6000E+03", "1.5742E+05"}, 
         {"3.7000E+03", "1.6995E+05"}, 
         {"3.8000E+03", "1.7777E+05"}, 
         {"3.9000E+03", "1.7950E+05"}, 
         {"4.0000E+03", "1.7463E+05"}, 
         {"4.1000E+03", "1.6360E+05"}, 
         {"4.2000E+03", "1.4864E+05"}, 
         {"4.3000E+03", "1.3122E+05"}, 
         {"4.4000E+03", "1.1348E+05"}, 
         {"4.5000E+03", "9.6869E+04"}, 
         {"4.6000E+03", "8.2223E+04"}, 
         {"4.7000E+03", "6.9849E+04"}, 
         {"4.8000E+03", "5.9704E+04"}, 
         {"4.9000E+03", "5.1554E+04"}, 
         {"5.0000E+03", "4.5094E+04"}, 
         {"5.1000E+03", "4.0014E+04"}, 
         {"5.2000E+03", "3.6037E+04"}, 
         {"5.3000E+03", "3.2928E+04"}, 
         {"5.4000E+03", "3.0496E+04"}, 
         {"5.5000E+03", "2.8593E+04"}, 
         {"5.6000E+03", "2.7099E+04"}, 
         {"5.7000E+03", "2.5925E+04"}, 
         {"5.8000E+03", "2.5000E+04"}, 
         {"5.9000E+03", "2.4272E+04"}, 
         {"6.0000E+03", "2.3701E+04"}, 
         {"6.1000E+03", "2.3254E+04"}, 
         {"6.2000E+03", "2.2908E+04"}, 
         {"6.3000E+03", "2.2645E+04"}, 
         {"6.4000E+03", "2.2452E+04"}, 
         {"6.5000E+03", "2.2318E+04"}, 
         {"6.6000E+03", "2.2235E+04"}, 
         {"6.7000E+03", "2.2198E+04"}, 
         {"6.8000E+03", "2.2204E+04"}, 
         {"6.9000E+03", "2.2249E+04"}, 
         {"7.0000E+03", "2.2331E+04"}, 
         {"7.1000E+03", "2.2452E+04"}, 
         {"7.2000E+03", "2.2597E+04"}, 
         {"7.3000E+03", "2.2793E+04"}, 
         {"7.4000E+03", "2.3022E+04"}, 
         {"7.5000E+03", "2.3278E+04"}, 
         {"7.6000E+03", "2.3595E+04"}, 
         {"7.7000E+03", "2.3946E+04"}, 
         {"7.8000E+03", "2.4340E+04"}, 
         {"7.9000E+03", "2.4782E+04"}, 
         {"8.0000E+03", "2.5305E+04"}, 
         {"8.1000E+03", "2.5821E+04"}, 
         {"8.2000E+03", "2.6419E+04"}, 
         {"8.3000E+03", "2.7074E+04"}, 
         {"8.4000E+03", "2.7789E+04"}, 
         {"8.5000E+03", "2.8646E+04"}, 
         {"8.6000E+03", "2.9425E+04"}, 
         {"8.7000E+03", "3.0341E+04"}, 
         {"8.8000E+03", "3.1455E+04"}, 
         {"8.9000E+03", "3.2412E+04"}, 
         {"9.0000E+03", "3.3729E+04"}, 
         {"9.1000E+03", "3.4807E+04"}, 
         {"9.2000E+03", "3.6353E+04"}, 
         {"9.3000E+03", "3.7555E+04"}, 
         {"9.4000E+03", "3.9355E+04"}, 
         {"9.5000E+03", "4.1037E+04"}, 
         {"9.6000E+03", "4.2410E+04"}, 
         {"9.7000E+03", "4.4668E+04"}, 
         {"9.8000E+03", "4.6159E+04"}, 
         {"9.9000E+03", "4.8749E+04"}, 
         {"1.0000E+04", "5.1015E+04"}, 
         {"1.0100E+04", "5.2644E+04"}, 
         {"1.0200E+04", "5.5828E+04"}, 
         {"1.0300E+04", "5.8490E+04"}, 
         {"1.0400E+04", "6.0221E+04"}, 
         {"1.0500E+04", "6.4090E+04"}, 
         {"1.0600E+04", "6.7175E+04"}, 
         {"1.0700E+04", "7.0414E+04"}, 
         {"1.0800E+04", "7.2156E+04"}, 
         {"1.0900E+04", "7.7139E+04"}, 
         {"1.1000E+04", "8.0830E+04"}, 
         {"1.1100E+04", "8.4682E+04"}, 
         {"1.1200E+04", "8.6290E+04"}, 
         {"1.1300E+04", "9.2583E+04"}, 
         {"1.1400E+04", "9.6900E+04"}, 
         {"1.1500E+04", "1.0138E+05"}, 
         {"1.1600E+04", "1.0602E+05"}, 
         {"1.1700E+04", "1.1083E+05"}, 
         {"1.1800E+04", "1.1169E+05"}, 
         {"1.1900E+04", "1.2049E+05"}, 
         {"1.2000E+04", "1.2573E+05"}, 
         {"1.2100E+04", "1.3112E+05"}, 
         {"1.2200E+04", "1.3665E+05"}, 
         {"1.2300E+04", "1.4231E+05"}, 
         {"1.2500E+04", "1.5346E+05"}, 
         {"1.2600E+04", "1.5944E+05"}, 
         {"1.2700E+04", "1.6552E+05"}, 
         {"1.2800E+04", "1.7167E+05"}, 
         {"1.2900E+04", "1.7789E+05"}, 
         {"1.3000E+04", "1.8415E+05"}, 
         {"1.3100E+04", "1.9044E+05"}, 
         {"1.3200E+04", "1.9674E+05"}, 
         {"1.3400E+04", "2.0862E+05"}, 
         {"1.3500E+04", "2.1479E+05"}, 
         {"1.3600E+04", "2.2088E+05"}, 
         {"1.3700E+04", "2.2685E+05"}, 
         {"1.3800E+04", "2.3268E+05"}, 
         {"1.3900E+04", "2.3833E+05"}, 
         {"1.4000E+04", "2.4377E+05"}, 
         {"1.4100E+04", "2.4898E+05"}, 
         {"1.4200E+04", "2.5392E+05"}, 
         {"1.4300E+04", "2.5856E+05"}, 
         {"1.4400E+04", "2.6286E+05"}, 
         {"1.4500E+04", "2.6681E+05"}, 
         {"1.4600E+04", "2.7037E+05"}, 
         {"1.4700E+04", "2.7351E+05"}, 
         {"1.4800E+04", "2.7622E+05"}, 
         {"1.4900E+04", "2.7846E+05"}, 
         {"1.5100E+04", "2.8143E+05"}, 
         {"1.5200E+04", "2.8227E+05"}, 
         {"1.5300E+04", "2.8260E+05"}, 
         {"1.5400E+04", "2.8243E+05"}, 
         {"1.5500E+04", "2.8175E+05"}, 
         {"1.5600E+04", "2.8056E+05"}, 
         {"1.5700E+04", "2.7889E+05"}, 
         {"1.5800E+04", "2.7674E+05"}, 
         {"1.5900E+04", "2.7414E+05"}, 
         {"1.6000E+04", "2.7110E+05"}, 
         {"1.6100E+04", "2.6765E+05"}, 
         {"1.6200E+04", "2.6381E+05"}, 
         {"1.6300E+04", "2.5963E+05"}, 
         {"1.6400E+04", "2.5513E+05"}, 
         {"1.6500E+04", "2.5034E+05"}, 
         {"1.6600E+04", "2.4530E+05"}, 
         {"1.6700E+04", "2.4004E+05"}, 
         {"1.6800E+04", "2.3461E+05"}, 
         {"1.6900E+04", "2.2902E+05"}, 
         {"1.7000E+04", "2.2332E+05"}, 
         {"1.7100E+04", "2.1754E+05"}, 
         {"1.7200E+04", "2.1171E+05"}, 
         {"1.7300E+04", "2.0585E+05"}, 
         {"1.7400E+04", "2.0000E+05"}, 
         {"1.7500E+04", "1.9418E+05"}, 
         {"1.7600E+04", "1.8840E+05"}, 
         {"1.7700E+04", "1.8270E+05"}, 
         {"1.7800E+04", "1.7709E+05"}, 
         {"1.7900E+04", "1.7158E+05"}, 
         {"1.8000E+04", "1.6618E+05"}, 
         {"1.8100E+04", "1.6092E+05"}, 
         {"1.8200E+04", "1.5478E+05"}, 
         {"1.8300E+04", "1.5019E+05"}, 
         {"1.8400E+04", "1.4538E+05"}, 
         {"1.8500E+04", "1.4074E+05"}, 
         {"1.8600E+04", "1.3625E+05"}, 
         {"1.8700E+04", "1.3193E+05"}, 
         {"1.8800E+04", "1.2776E+05"}, 
         {"1.8900E+04", "1.2376E+05"}, 
         {"1.9000E+04", "1.1992E+05"}, 
         {"1.9100E+04", "1.1624E+05"}, 
         {"1.9200E+04", "1.1271E+05"}, 
         {"1.9300E+04", "1.0934E+05"}, 
         {"1.9400E+04", "1.0611E+05"}, 
         {"1.9500E+04", "1.0303E+05"}, 
         {"1.9600E+04", "1.0009E+05"}, 
         {"1.9700E+04", "9.7283E+04"}, 
         {"1.9800E+04", "9.4610E+04"}, 
         {"1.9900E+04", "9.2064E+04"}, 
         {"2.0000E+04", "8.9639E+04"}, 
         {"2.0100E+04", "8.7331E+04"}, 
         {"2.0200E+04", "8.5136E+04"}, 
         {"2.0300E+04", "8.3048E+04"}, 
         {"2.0400E+04", "8.1064E+04"}, 
         {"2.0500E+04", "7.9177E+04"}, 
         {"2.0600E+04", "7.7384E+04"}, 
         {"2.0700E+04", "7.5681E+04"}, 
         {"2.0800E+04", "7.4066E+04"}, 
         {"2.0900E+04", "7.2527E+04"}, 
         {"2.1000E+04", "7.1087E+04"}, 
         {"2.1100E+04", "6.9681E+04"}, 
         {"2.1200E+04", "6.8365E+04"}, 
         {"2.1300E+04", "6.7116E+04"}, 
         {"2.1400E+04", "6.5929E+04"}, 
         {"2.1500E+04", "6.4802E+04"}, 
         {"2.1600E+04", "6.3732E+04"}, 
         {"2.1700E+04", "6.2715E+04"}, 
         {"2.1800E+04", "6.1750E+04"}, 
         {"2.1900E+04", "6.0833E+04"}, 
         {"2.2000E+04", "5.9962E+04"}, 
         {"2.2200E+04", "5.8319E+04"}, 
         {"2.2300E+04", "5.7573E+04"}, 
         {"2.2400E+04", "5.6869E+04"}, 
         {"2.2500E+04", "5.6199E+04"}, 
         {"2.2600E+04", "5.5562E+04"}, 
         {"2.2700E+04", "5.4955E+04"}, 
         {"2.2800E+04", "5.4379E+04"}, 
         {"2.2900E+04", "5.3830E+04"}, 
         {"2.3000E+04", "5.3308E+04"}, 
         {"2.3100E+04", "5.2811E+04"}, 
         {"2.3200E+04", "5.2338E+04"}, 
         {"2.3300E+04", "5.1887E+04"}, 
         {"2.3400E+04", "5.1458E+04"}, 
         {"2.3500E+04", "5.1049E+04"}, 
         {"2.3600E+04", "5.0660E+04"}, 
         {"2.3700E+04", "5.0288E+04"}, 
         {"2.3800E+04", "4.9934E+04"}, 
         {"2.3900E+04", "4.9597E+04"}, 
         {"2.4000E+04", "4.9275E+04"}});

    return model;
  }

  public static Model run2(Model model) {
    model.component("comp1").material("mat1").propertyGroup("def").func("int2").set("interp", "piecewisecubic");
    model.component("comp1").material("mat1").propertyGroup("def").func("int2").set("extrap", "linear");
    model.component("comp1").material("mat1").propertyGroup("def").func("int2")
         .set("fununit", new String[]{"J/kg/K"});
    model.component("comp1").material("mat1").propertyGroup("def").func("int2").set("argunit", new String[]{"K"});
    model.component("comp1").material("mat1").propertyGroup("def").func("int3").set("funcname", "mu");
    model.component("comp1").material("mat1").propertyGroup("def").func("int3")
         .set("table", new String[][]{{"5.0000E+02", "1.2055E-05"}, 
         {"6.0000E+02", "1.3775E-05"}, 
         {"7.0000E+02", "1.5435E-05"}, 
         {"8.0000E+02", "1.7042E-05"}, 
         {"9.0000E+02", "1.8605E-05"}, 
         {"1.0000E+03", "2.0132E-05"}, 
         {"1.1000E+03", "2.1626E-05"}, 
         {"1.2000E+03", "2.3094E-05"}, 
         {"1.3000E+03", "2.4537E-05"}, 
         {"1.4000E+03", "2.5960E-05"}, 
         {"1.5000E+03", "2.7363E-05"}, 
         {"1.6000E+03", "2.8748E-05"}, 
         {"1.7000E+03", "3.0118E-05"}, 
         {"1.8000E+03", "3.1474E-05"}, 
         {"1.9000E+03", "3.2817E-05"}, 
         {"2.0000E+03", "3.4148E-05"}, 
         {"2.1000E+03", "3.5470E-05"}, 
         {"2.2000E+03", "3.6784E-05"}, 
         {"2.3000E+03", "3.8092E-05"}, 
         {"2.4000E+03", "3.9399E-05"}, 
         {"2.5000E+03", "4.0707E-05"}, 
         {"2.6000E+03", "4.2019E-05"}, 
         {"2.7000E+03", "4.3336E-05"}, 
         {"2.8000E+03", "4.4656E-05"}, 
         {"2.9000E+03", "4.5970E-05"}, 
         {"3.0000E+03", "4.7260E-05"}, 
         {"3.1000E+03", "4.8496E-05"}, 
         {"3.2000E+03", "4.9635E-05"}, 
         {"3.3000E+03", "5.0622E-05"}, 
         {"3.4000E+03", "5.1397E-05"}, 
         {"3.5000E+03", "5.1904E-05"}, 
         {"3.6000E+03", "5.2110E-05"}, 
         {"3.7000E+03", "5.2018E-05"}, 
         {"3.8000E+03", "5.1670E-05"}, 
         {"3.9000E+03", "5.1146E-05"}, 
         {"4.0000E+03", "5.0545E-05"}, 
         {"4.1000E+03", "4.9964E-05"}, 
         {"4.2000E+03", "4.9482E-05"}, 
         {"4.3000E+03", "4.9148E-05"}, 
         {"4.4000E+03", "4.8984E-05"}, 
         {"4.5000E+03", "4.8987E-05"}, 
         {"4.6000E+03", "4.9146E-05"}, 
         {"4.7000E+03", "4.9439E-05"}, 
         {"4.8000E+03", "4.9845E-05"}, 
         {"4.9000E+03", "5.0343E-05"}, 
         {"5.0000E+03", "5.0916E-05"}, 
         {"5.1000E+03", "5.1549E-05"}, 
         {"5.2000E+03", "5.2229E-05"}, 
         {"5.3000E+03", "5.2947E-05"}, 
         {"5.4000E+03", "5.3695E-05"}, 
         {"5.5000E+03", "5.4467E-05"}, 
         {"5.6000E+03", "5.5258E-05"}, 
         {"5.7000E+03", "5.6063E-05"}, 
         {"5.8000E+03", "5.6882E-05"}, 
         {"5.9000E+03", "5.7710E-05"}, 
         {"6.0000E+03", "5.8545E-05"}, 
         {"6.1000E+03", "5.9388E-05"}, 
         {"6.2000E+03", "6.0235E-05"}, 
         {"6.3000E+03", "6.1086E-05"}, 
         {"6.4000E+03", "6.1940E-05"}, 
         {"6.5000E+03", "6.2797E-05"}, 
         {"6.6000E+03", "6.3656E-05"}, 
         {"6.7000E+03", "6.4515E-05"}, 
         {"6.8000E+03", "6.5375E-05"}, 
         {"6.9000E+03", "6.6235E-05"}, 
         {"7.0000E+03", "6.7094E-05"}, 
         {"7.1000E+03", "6.7953E-05"}, 
         {"7.2000E+03", "6.8809E-05"}, 
         {"7.3000E+03", "6.9663E-05"}, 
         {"7.4000E+03", "7.0514E-05"}, 
         {"7.5000E+03", "7.1361E-05"}, 
         {"7.6000E+03", "7.2204E-05"}, 
         {"7.7000E+03", "7.3041E-05"}, 
         {"7.8000E+03", "7.3872E-05"}, 
         {"7.9000E+03", "7.4696E-05"}, 
         {"8.0000E+03", "7.5511E-05"}, 
         {"8.1000E+03", "7.6317E-05"}, 
         {"8.3000E+03", "7.7895E-05"}, 
         {"8.4000E+03", "7.8663E-05"}, 
         {"8.5000E+03", "7.9416E-05"}, 
         {"8.6000E+03", "8.0151E-05"}, 
         {"8.7000E+03", "8.0867E-05"}, 
         {"8.8000E+03", "8.1560E-05"}, 
         {"8.9000E+03", "8.2229E-05"}, 
         {"9.0000E+03", "8.2870E-05"}, 
         {"9.1000E+03", "8.3482E-05"}, 
         {"9.2000E+03", "8.4061E-05"}, 
         {"9.3000E+03", "8.4603E-05"}, 
         {"9.4000E+03", "8.5105E-05"}, 
         {"9.5000E+03", "8.5564E-05"}, 
         {"9.6000E+03", "8.5976E-05"}, 
         {"9.7000E+03", "8.6337E-05"}, 
         {"9.8000E+03", "8.6642E-05"}, 
         {"9.9000E+03", "8.6889E-05"}, 
         {"1.0000E+04", "8.7011E-05"}, 
         {"1.0100E+04", "8.7187E-05"}, 
         {"1.0200E+04", "8.7230E-05"}, 
         {"1.0300E+04", "8.7198E-05"}, 
         {"1.0400E+04", "8.7085E-05"}, 
         {"1.0500E+04", "8.6890E-05"}, 
         {"1.0600E+04", "8.6608E-05"}, 
         {"1.0700E+04", "8.6237E-05"}, 
         {"1.0800E+04", "8.5773E-05"}, 
         {"1.0900E+04", "8.5216E-05"}, 
         {"1.1000E+04", "8.4564E-05"}, 
         {"1.1100E+04", "8.3816E-05"}, 
         {"1.1200E+04", "8.2970E-05"}, 
         {"1.1300E+04", "8.2030E-05"}, 
         {"1.1400E+04", "8.0997E-05"}, 
         {"1.1500E+04", "7.9873E-05"}, 
         {"1.1600E+04", "7.8661E-05"}, 
         {"1.1700E+04", "7.7365E-05"}, 
         {"1.1800E+04", "7.5983E-05"}, 
         {"1.1900E+04", "7.4531E-05"}, 
         {"1.2000E+04", "7.3010E-05"}, 
         {"1.2100E+04", "7.1427E-05"}, 
         {"1.2200E+04", "6.9788E-05"}, 
         {"1.2300E+04", "6.8100E-05"}, 
         {"1.2400E+04", "6.6359E-05"}, 
         {"1.2500E+04", "6.4594E-05"}, 
         {"1.2600E+04", "6.2803E-05"}, 
         {"1.2700E+04", "6.0992E-05"}, 
         {"1.2800E+04", "5.9170E-05"}, 
         {"1.2900E+04", "5.7343E-05"}, 
         {"1.3000E+04", "5.5517E-05"}, 
         {"1.3100E+04", "5.3700E-05"}, 
         {"1.3200E+04", "5.1897E-05"}, 
         {"1.3300E+04", "5.0088E-05"}, 
         {"1.3400E+04", "4.8327E-05"}, 
         {"1.3500E+04", "4.6596E-05"}, 
         {"1.3600E+04", "4.4899E-05"}, 
         {"1.3700E+04", "4.3239E-05"}, 
         {"1.3800E+04", "4.1619E-05"}, 
         {"1.3900E+04", "4.0042E-05"}, 
         {"1.4000E+04", "3.8510E-05"}, 
         {"1.4100E+04", "3.7026E-05"}, 
         {"1.4200E+04", "3.5589E-05"}, 
         {"1.4300E+04", "3.4202E-05"}, 
         {"1.4400E+04", "3.2865E-05"}, 
         {"1.4500E+04", "3.1579E-05"}, 
         {"1.4600E+04", "3.0343E-05"}, 
         {"1.4700E+04", "2.9157E-05"}, 
         {"1.4800E+04", "2.8021E-05"}, 
         {"1.4900E+04", "2.6935E-05"}, 
         {"1.5000E+04", "2.5837E-05"}, 
         {"1.5100E+04", "2.4844E-05"}, 
         {"1.5200E+04", "2.3899E-05"}, 
         {"1.5300E+04", "2.2999E-05"}, 
         {"1.5400E+04", "2.2143E-05"}, 
         {"1.5500E+04", "2.1331E-05"}, 
         {"1.5600E+04", "2.0561E-05"}, 
         {"1.5700E+04", "1.9830E-05"}, 
         {"1.5800E+04", "1.9139E-05"}, 
         {"1.5900E+04", "1.8486E-05"}, 
         {"1.6000E+04", "1.7868E-05"}, 
         {"1.6100E+04", "1.7285E-05"}, 
         {"1.6200E+04", "1.6736E-05"}, 
         {"1.6300E+04", "1.6218E-05"}, 
         {"1.6400E+04", "1.5731E-05"}, 
         {"1.6500E+04", "1.5273E-05"}, 
         {"1.6600E+04", "1.4844E-05"}, 
         {"1.6700E+04", "1.4440E-05"}, 
         {"1.6800E+04", "1.4062E-05"}, 
         {"1.6900E+04", "1.3708E-05"}, 
         {"1.7000E+04", "1.3377E-05"}, 
         {"1.7100E+04", "1.3068E-05"}, 
         {"1.7200E+04", "1.2779E-05"}, 
         {"1.7300E+04", "1.2510E-05"}, 
         {"1.7400E+04", "1.2260E-05"}, 
         {"1.7500E+04", "1.2027E-05"}, 
         {"1.7600E+04", "1.1812E-05"}, 
         {"1.7700E+04", "1.1612E-05"}, 
         {"1.7800E+04", "1.1427E-05"}, 
         {"1.7900E+04", "1.1256E-05"}, 
         {"1.8000E+04", "1.1099E-05"}, 
         {"1.8100E+04", "1.0955E-05"}, 
         {"1.8200E+04", "1.0920E-05"}, 
         {"1.8300E+04", "1.0799E-05"}, 
         {"1.8400E+04", "1.0689E-05"}, 
         {"1.8500E+04", "1.0590E-05"}, 
         {"1.8600E+04", "1.0500E-05"}, 
         {"1.8700E+04", "1.0419E-05"}, 
         {"1.8800E+04", "1.0347E-05"}, 
         {"1.8900E+04", "1.0284E-05"}, 
         {"1.9000E+04", "1.0228E-05"}, 
         {"1.9100E+04", "1.0179E-05"}, 
         {"1.9200E+04", "1.0137E-05"}, 
         {"1.9300E+04", "1.0102E-05"}, 
         {"1.9400E+04", "1.0074E-05"}, 
         {"1.9500E+04", "1.0051E-05"}, 
         {"1.9600E+04", "1.0034E-05"}, 
         {"1.9700E+04", "1.0022E-05"}, 
         {"1.9800E+04", "1.0015E-05"}, 
         {"1.9900E+04", "1.0013E-05"}, 
         {"2.0000E+04", "1.0016E-05"}, 
         {"2.0100E+04", "1.0023E-05"}, 
         {"2.0200E+04", "1.0034E-05"}, 
         {"2.0300E+04", "1.0050E-05"}, 
         {"2.0400E+04", "1.0068E-05"}, 
         {"2.0500E+04", "1.0091E-05"}, 
         {"2.0600E+04", "1.0117E-05"}, 
         {"2.0700E+04", "1.0146E-05"}, 
         {"2.0800E+04", "1.0179E-05"}, 
         {"2.0900E+04", "1.0214E-05"}, 
         {"2.1000E+04", "1.0252E-05"}, 
         {"2.1100E+04", "1.0293E-05"}, 
         {"2.1200E+04", "1.0337E-05"}, 
         {"2.1300E+04", "1.0383E-05"}, 
         {"2.1400E+04", "1.0431E-05"}, 
         {"2.1500E+04", "1.0482E-05"}, 
         {"2.1600E+04", "1.0535E-05"}, 
         {"2.1700E+04", "1.0590E-05"}, 
         {"2.1800E+04", "1.0647E-05"}, 
         {"2.1900E+04", "1.0706E-05"}, 
         {"2.2000E+04", "1.0767E-05"}, 
         {"2.2100E+04", "1.0932E-05"}, 
         {"2.2200E+04", "1.0996E-05"}, 
         {"2.2300E+04", "1.1062E-05"}, 
         {"2.2400E+04", "1.1129E-05"}, 
         {"2.2500E+04", "1.1198E-05"}, 
         {"2.2600E+04", "1.1269E-05"}, 
         {"2.2700E+04", "1.1341E-05"}, 
         {"2.2800E+04", "1.1415E-05"}, 
         {"2.2900E+04", "1.1490E-05"}, 
         {"2.3000E+04", "1.1566E-05"}, 
         {"2.3100E+04", "1.1644E-05"}, 
         {"2.3200E+04", "1.1722E-05"}, 
         {"2.3300E+04", "1.1803E-05"}, 
         {"2.3400E+04", "1.1884E-05"}, 
         {"2.3500E+04", "1.1966E-05"}, 
         {"2.3600E+04", "1.2050E-05"}, 
         {"2.3700E+04", "1.2135E-05"}, 
         {"2.3800E+04", "1.2221E-05"}, 
         {"2.3900E+04", "1.2308E-05"}, 
         {"2.4000E+04", "1.2396E-05"}});
    model.component("comp1").material("mat1").propertyGroup("def").func("int3").set("interp", "piecewisecubic");
    model.component("comp1").material("mat1").propertyGroup("def").func("int3").set("extrap", "linear");
    model.component("comp1").material("mat1").propertyGroup("def").func("int3").set("fununit", new String[]{"Pa*s"});
    model.component("comp1").material("mat1").propertyGroup("def").func("int3").set("argunit", new String[]{"K"});
    model.component("comp1").material("mat1").propertyGroup("def").func("int4").set("funcname", "k");
    model.component("comp1").material("mat1").propertyGroup("def").func("int4")
         .set("table", new String[][]{{"5.0000E+02", "2.5776E-01"}, 
         {"6.0000E+02", "2.9747E-01"}, 
         {"7.0000E+02", "3.3676E-01"}, 
         {"8.0000E+02", "3.7576E-01"}, 
         {"9.0000E+02", "4.1462E-01"}, 
         {"1.0000E+03", "4.5350E-01"}, 
         {"1.1000E+03", "4.9250E-01"}, 
         {"1.2000E+03", "5.3169E-01"}, 
         {"1.3000E+03", "5.7117E-01"}, 
         {"1.4000E+03", "6.1114E-01"}, 
         {"1.5000E+03", "6.5205E-01"}, 
         {"1.6000E+03", "6.9487E-01"}, 
         {"1.7000E+03", "7.4152E-01"}, 
         {"1.8000E+03", "7.9535E-01"}, 
         {"1.9000E+03", "8.6174E-01"}, 
         {"2.0000E+03", "9.4869E-01"}, 
         {"2.1000E+03", "1.0673E+00"}, 
         {"2.2000E+03", "1.2323E+00"}, 
         {"2.3000E+03", "1.4619E+00"}, 
         {"2.4000E+03", "1.7776E+00"}, 
         {"2.5000E+03", "2.2036E+00"}, 
         {"2.6000E+03", "2.7655E+00"}, 
         {"2.7000E+03", "3.4882E+00"}, 
         {"2.8000E+03", "4.3932E+00"}, 
         {"2.9000E+03", "5.4944E+00"}, 
         {"3.0000E+03", "6.7934E+00"}, 
         {"3.1000E+03", "8.2730E+00"}, 
         {"3.2000E+03", "9.8906E+00"}, 
         {"3.3000E+03", "1.1572E+01"}, 
         {"3.4000E+03", "1.3208E+01"}, 
         {"3.5000E+03", "1.4660E+01"}, 
         {"3.6000E+03", "1.5770E+01"}, 
         {"3.7000E+03", "1.6395E+01"}, 
         {"3.8000E+03", "1.6440E+01"}, 
         {"3.9000E+03", "1.5892E+01"}, 
         {"4.0000E+03", "1.4830E+01"}, 
         {"4.1000E+03", "1.3406E+01"}, 
         {"4.2000E+03", "1.1802E+01"}, 
         {"4.3000E+03", "1.0185E+01"}, 
         {"4.4000E+03", "8.6772E+00"}, 
         {"4.5000E+03", "7.3487E+00"}, 
         {"4.6000E+03", "6.2253E+00"}, 
         {"4.7000E+03", "5.3030E+00"}, 
         {"4.8000E+03", "4.5613E+00"}, 
         {"4.9000E+03", "3.9734E+00"}, 
         {"5.0000E+03", "3.5120E+00"}, 
         {"5.1000E+03", "3.1526E+00"}, 
         {"5.2000E+03", "2.8740E+00"}, 
         {"5.3000E+03", "2.6590E+00"}, 
         {"5.4000E+03", "2.4941E+00"}, 
         {"5.5000E+03", "2.3683E+00"}, 
         {"5.6000E+03", "2.2732E+00"}, 
         {"5.7000E+03", "2.2022E+00"}, 
         {"5.8000E+03", "2.1504E+00"}, 
         {"5.9000E+03", "2.1137E+00"}, 
         {"6.0000E+03", "2.0890E+00"}, 
         {"6.1000E+03", "2.0741E+00"}, 
         {"6.2000E+03", "2.0670E+00"}, 
         {"6.3000E+03", "2.0663E+00"}, 
         {"6.4000E+03", "2.0709E+00"}, 
         {"6.5000E+03", "2.0799E+00"}, 
         {"6.6000E+03", "2.0927E+00"}, 
         {"6.7000E+03", "2.1086E+00"}, 
         {"6.8000E+03", "2.1274E+00"}, 
         {"6.9000E+03", "2.1486E+00"}, 
         {"7.0000E+03", "2.1721E+00"}, 
         {"7.1000E+03", "2.1976E+00"}, 
         {"7.2000E+03", "2.2248E+00"}, 
         {"7.3000E+03", "2.2540E+00"}, 
         {"7.4000E+03", "2.2849E+00"}, 
         {"7.5000E+03", "2.3171E+00"}, 
         {"7.6000E+03", "2.3514E+00"}, 
         {"7.7000E+03", "2.3873E+00"}, 
         {"7.8000E+03", "2.4249E+00"}, 
         {"7.9000E+03", "2.4642E+00"}, 
         {"8.0000E+03", "2.5061E+00"}, 
         {"8.1000E+03", "2.5490E+00"}, 
         {"8.2000E+03", "2.5936E+00"}, 
         {"8.3000E+03", "2.6400E+00"}, 
         {"8.4000E+03", "2.6882E+00"}, 
         {"8.5000E+03", "2.7401E+00"}, 
         {"8.6000E+03", "2.7920E+00"}, 
         {"8.7000E+03", "2.8457E+00"}, 
         {"8.8000E+03", "2.9039E+00"}, 
         {"8.9000E+03", "2.9612E+00"}, 
         {"9.0000E+03", "3.0237E+00"}, 
         {"9.1000E+03", "3.0845E+00"}, 
         {"9.2000E+03", "3.1514E+00"}, 
         {"9.3000E+03", "3.2152E+00"}, 
         {"9.4000E+03", "3.2862E+00"}, 
         {"9.5000E+03", "3.3596E+00"}, 
         {"9.6000E+03", "3.4274E+00"}, 
         {"9.7000E+03", "3.5044E+00"}, 
         {"9.8000E+03", "3.5741E+00"}, 
         {"9.9000E+03", "3.6542E+00"}, 
         {"1.0000E+04", "3.7364E+00"}, 
         {"1.0100E+04", "3.8078E+00"}, 
         {"1.0200E+04", "3.8922E+00"}, 
         {"1.0300E+04", "3.9784E+00"}, 
         {"1.0400E+04", "4.0499E+00"}, 
         {"1.0500E+04", "4.1374E+00"}, 
         {"1.0600E+04", "4.2263E+00"}, 
         {"1.0700E+04", "4.3165E+00"}, 
         {"1.0800E+04", "4.3860E+00"}, 
         {"1.0900E+04", "4.4764E+00"}, 
         {"1.1000E+04", "4.5678E+00"}, 
         {"1.1100E+04", "4.6602E+00"}, 
         {"1.1200E+04", "4.7260E+00"}, 
         {"1.1300E+04", "4.8180E+00"}, 
         {"1.1400E+04", "4.9107E+00"}, 
         {"1.1500E+04", "5.0042E+00"}, 
         {"1.1600E+04", "5.0985E+00"}, 
         {"1.1700E+04", "5.1936E+00"}, 
         {"1.1800E+04", "5.2531E+00"}, 
         {"1.1900E+04", "5.3476E+00"}, 
         {"1.2000E+04", "5.4429E+00"}, 
         {"1.2100E+04", "5.5390E+00"}, 
         {"1.2200E+04", "5.6357E+00"}, 
         {"1.2300E+04", "5.7330E+00"}, 
         {"1.2400E+04", "5.7885E+00"}, 
         {"1.2500E+04", "5.8852E+00"}, 
         {"1.2600E+04", "5.9822E+00"}, 
         {"1.2700E+04", "6.0793E+00"}, 
         {"1.2800E+04", "6.1764E+00"}, 
         {"1.2900E+04", "6.2730E+00"}, 
         {"1.3000E+04", "6.3690E+00"}, 
         {"1.3100E+04", "6.4638E+00"}, 
         {"1.3200E+04", "6.5573E+00"}, 
         {"1.3300E+04", "6.6034E+00"}, 
         {"1.3400E+04", "6.6923E+00"}, 
         {"1.3500E+04", "6.7784E+00"}, 
         {"1.3600E+04", "6.8614E+00"}, 
         {"1.3700E+04", "6.9406E+00"}, 
         {"1.3800E+04", "7.0155E+00"}, 
         {"1.3900E+04", "7.0856E+00"}, 
         {"1.4000E+04", "7.1503E+00"}, 
         {"1.4100E+04", "7.2091E+00"}, 
         {"1.4200E+04", "7.2615E+00"}, 
         {"1.4300E+04", "7.3069E+00"}, 
         {"1.4400E+04", "7.3451E+00"}, 
         {"1.4500E+04", "7.3755E+00"}, 
         {"1.4600E+04", "7.3979E+00"}, 
         {"1.4700E+04", "7.4120E+00"}, 
         {"1.4800E+04", "7.4174E+00"}, 
         {"1.4900E+04", "7.4142E+00"}, 
         {"1.5000E+04", "7.3773E+00"}, 
         {"1.5100E+04", "7.3583E+00"}, 
         {"1.5200E+04", "7.3306E+00"}, 
         {"1.5300E+04", "7.2945E+00"}, 
         {"1.5400E+04", "7.2495E+00"}, 
         {"1.5500E+04", "7.1972E+00"}, 
         {"1.5600E+04", "7.1372E+00"}, 
         {"1.5700E+04", "7.0701E+00"}, 
         {"1.5800E+04", "6.9962E+00"}, 
         {"1.5900E+04", "6.9161E+00"}, 
         {"1.6000E+04", "6.8305E+00"}, 
         {"1.6100E+04", "6.7398E+00"}, 
         {"1.6200E+04", "6.6448E+00"}, 
         {"1.6300E+04", "6.5459E+00"}, 
         {"1.6400E+04", "6.4440E+00"}, 
         {"1.6500E+04", "6.3396E+00"}, 
         {"1.6600E+04", "6.2334E+00"}, 
         {"1.6700E+04", "6.1259E+00"}, 
         {"1.6800E+04", "6.0177E+00"}, 
         {"1.6900E+04", "5.9095E+00"}, 
         {"1.7000E+04", "5.8017E+00"}, 
         {"1.7100E+04", "5.6947E+00"}, 
         {"1.7200E+04", "5.5892E+00"}, 
         {"1.7300E+04", "5.4854E+00"}, 
         {"1.7400E+04", "5.3837E+00"}, 
         {"1.7500E+04", "5.2845E+00"}, 
         {"1.7600E+04", "5.1880E+00"}, 
         {"1.7700E+04", "5.0945E+00"}, 
         {"1.7800E+04", "5.0041E+00"}, 
         {"1.7900E+04", "4.9171E+00"}, 
         {"1.8000E+04", "4.8335E+00"}, 
         {"1.8100E+04", "4.7535E+00"}, 
         {"1.8200E+04", "4.6736E+00"}, 
         {"1.8300E+04", "4.6010E+00"}, 
         {"1.8400E+04", "4.5321E+00"}, 
         {"1.8500E+04", "4.4669E+00"}, 
         {"1.8600E+04", "4.4054E+00"}, 
         {"1.8700E+04", "4.3475E+00"}, 
         {"1.8800E+04", "4.2931E+00"}, 
         {"1.8900E+04", "4.2423E+00"}, 
         {"1.9000E+04", "4.1949E+00"}, 
         {"1.9100E+04", "4.1509E+00"}, 
         {"1.9200E+04", "4.1101E+00"}, 
         {"1.9300E+04", "4.0725E+00"}, 
         {"1.9400E+04", "4.0379E+00"}, 
         {"1.9500E+04", "4.0063E+00"}, 
         {"1.9600E+04", "3.9775E+00"}, 
         {"1.9700E+04", "3.9514E+00"}, 
         {"1.9800E+04", "3.9280E+00"}, 
         {"1.9900E+04", "3.9071E+00"}, 
         {"2.0000E+04", "3.8886E+00"}, 
         {"2.0100E+04", "3.8724E+00"}, 
         {"2.0200E+04", "3.8584E+00"}, 
         {"2.0300E+04", "3.8465E+00"}, 
         {"2.0400E+04", "3.8366E+00"}, 
         {"2.0500E+04", "3.8286E+00"}, 
         {"2.0600E+04", "3.8225E+00"}, 
         {"2.0700E+04", "3.8180E+00"}, 
         {"2.0800E+04", "3.8152E+00"}, 
         {"2.0900E+04", "3.8140E+00"}, 
         {"2.1000E+04", "3.8142E+00"}, 
         {"2.1100E+04", "3.8159E+00"}, 
         {"2.1200E+04", "3.8189E+00"}, 
         {"2.1300E+04", "3.8231E+00"}, 
         {"2.1400E+04", "3.8285E+00"}, 
         {"2.1500E+04", "3.8351E+00"}, 
         {"2.1600E+04", "3.8427E+00"}, 
         {"2.1700E+04", "3.8513E+00"}, 
         {"2.1800E+04", "3.8608E+00"}, 
         {"2.1900E+04", "3.8713E+00"}, 
         {"2.2000E+04", "3.8825E+00"}, 
         {"2.2100E+04", "3.8807E+00"}, 
         {"2.2200E+04", "3.8926E+00"}, 
         {"2.2300E+04", "3.9051E+00"}, 
         {"2.2400E+04", "3.9163E+00"}, 
         {"2.2500E+04", "3.9319E+00"}, 
         {"2.2600E+04", "3.9461E+00"}, 
         {"2.2700E+04", "3.9608E+00"}, 
         {"2.2800E+04", "3.9759E+00"}, 
         {"2.2900E+04", "3.9914E+00"}, 
         {"2.3000E+04", "4.0073E+00"}, 
         {"2.3100E+04", "4.0235E+00"}, 
         {"2.3200E+04", "4.0400E+00"}, 
         {"2.3300E+04", "4.0561E+00"}, 
         {"2.3400E+04", "4.0737E+00"}, 
         {"2.3500E+04", "4.0909E+00"}, 
         {"2.3600E+04", "4.1083E+00"}, 
         {"2.3700E+04", "4.1259E+00"}, 
         {"2.3800E+04", "4.1435E+00"}, 
         {"2.3900E+04", "4.1613E+00"}, 
         {"2.4000E+04", "4.1791E+00"}});
    model.component("comp1").material("mat1").propertyGroup("def").func("int4").set("interp", "piecewisecubic");
    model.component("comp1").material("mat1").propertyGroup("def").func("int4").set("extrap", "linear");
    model.component("comp1").material("mat1").propertyGroup("def").func("int4").set("fununit", new String[]{"W/m/K"});
    model.component("comp1").material("mat1").propertyGroup("def").func("int4").set("argunit", new String[]{"K"});
    model.component("comp1").material("mat1").propertyGroup("def").func("int5").set("funcname", "sigma");
    model.component("comp1").material("mat1").propertyGroup("def").func("int5")
         .set("table", new String[][]{{"5.0000E+02", "1.6334E-24"}, 
         {"6.0000E+02", "1.4800E-24"}, 
         {"7.0000E+02", "1.3007E-24"}, 
         {"8.0000E+02", "1.1751E-24"}, 
         {"9.0000E+02", "1.0832E-24"}, 
         {"1.0000E+03", "1.0105E-24"}, 
         {"1.1000E+03", "9.4923E-25"}, 
         {"1.2000E+03", "3.3235E-24"}, 
         {"1.3000E+03", "2.0710E-23"}, 
         {"1.4000E+03", "2.8983E-21"}, 
         {"1.5000E+03", "2.4443E-19"}, 
         {"1.6000E+03", "1.1888E-17"}, 
         {"1.7000E+03", "3.6555E-16"}, 
         {"1.8000E+03", "7.7048E-15"}, 
         {"1.9000E+03", "1.1796E-13"}, 
         {"2.0000E+03", "1.3757E-12"}, 
         {"2.1000E+03", "1.2701E-11"}, 
         {"2.2000E+03", "9.5760E-11"}, 
         {"2.3000E+03", "6.0491E-10"}, 
         {"2.4000E+03", "3.2696E-09"}, 
         {"2.5000E+03", "1.5389E-08"}, 
         {"2.6000E+03", "6.3998E-08"}, 
         {"2.7000E+03", "2.3811E-07"}, 
         {"2.8000E+03", "8.0105E-07"}, 
         {"2.9000E+03", "2.4596E-06"}, 
         {"3.0000E+03", "6.9504E-06"}, 
         {"3.1000E+03", "1.8213E-05"}, 
         {"3.2000E+03", "4.4568E-05"}, 
         {"3.3000E+03", "1.0251E-04"}, 
         {"3.4000E+03", "2.2296E-04"}, 
         {"3.5000E+03", "4.6113E-04"}, 
         {"3.6000E+03", "9.1166E-04"}, 
         {"3.7000E+03", "1.7306E-03"}, 
         {"3.8000E+03", "3.1670E-03"}, 
         {"3.9000E+03", "5.6088E-03"}, 
         {"4.0000E+03", "9.6400E-03"}, 
         {"4.1000E+03", "1.6123E-02"}, 
         {"4.2000E+03", "2.6303E-02"}, 
         {"4.3000E+03", "4.1939E-02"}, 
         {"4.4000E+03", "6.5456E-02"}, 
         {"4.5000E+03", "1.0021E-01"}, 
         {"4.6000E+03", "1.5061E-01"}, 
         {"4.7000E+03", "2.2241E-01"}, 
         {"4.8000E+03", "3.2337E-01"}, 
         {"4.9000E+03", "4.6319E-01"}, 
         {"5.0000E+03", "6.5421E-01"}, 
         {"5.1000E+03", "9.1185E-01"}, 
         {"5.2000E+03", "1.2552E+00"}, 
         {"5.3000E+03", "1.7075E+00"}, 
         {"5.4000E+03", "2.2971E+00"}, 
         {"5.5000E+03", "3.0576E+00"}, 
         {"5.6000E+03", "4.0292E+00"}, 
         {"5.8000E+03", "6.8011E+00"}, 
         {"5.9000E+03", "8.7193E+00"}, 
         {"6.0000E+03", "1.1085E+01"}, 
         {"6.1000E+03", "1.3981E+01"}, 
         {"6.2000E+03", "1.7498E+01"}, 
         {"6.3000E+03", "2.1737E+01"}, 
         {"6.4000E+03", "2.6813E+01"}, 
         {"6.5000E+03", "3.2847E+01"}, 
         {"6.6000E+03", "3.9973E+01"}, 
         {"6.7000E+03", "4.8335E+01"}, 
         {"6.8000E+03", "5.8086E+01"}, 
         {"6.9000E+03", "6.9388E+01"}, 
         {"7.0000E+03", "8.2411E+01"}, 
         {"7.1000E+03", "9.7331E+01"}, 
         {"7.2000E+03", "1.1433E+02"}, 
         {"7.3000E+03", "1.3359E+02"}, 
         {"7.4000E+03", "1.5530E+02"}, 
         {"7.5000E+03", "1.7965E+02"}, 
         {"7.6000E+03", "2.0682E+02"}, 
         {"7.7000E+03", "2.3699E+02"}, 
         {"7.8000E+03", "2.7033E+02"}, 
         {"7.9000E+03", "3.0699E+02"}, 
         {"8.0000E+03", "3.4714E+02"}, 
         {"8.1000E+03", "3.9089E+02"}, 
         {"8.2000E+03", "4.3834E+02"}, 
         {"8.3000E+03", "4.8963E+02"}, 
         {"8.4000E+03", "5.4481E+02"}, 
         {"8.5000E+03", "6.0393E+02"}, 
         {"8.6000E+03", "6.6702E+02"}, 
         {"8.7000E+03", "7.3408E+02"}, 
         {"8.8000E+03", "8.0508E+02"}, 
         {"8.9000E+03", "8.7999E+02"}, 
         {"9.0000E+03", "9.5873E+02"}, 
         {"9.1000E+03", "1.0412E+03"}, 
         {"9.2000E+03", "1.1273E+03"}, 
         {"9.3000E+03", "1.2169E+03"}, 
         {"9.4000E+03", "1.3098E+03"}, 
         {"9.5000E+03", "1.4059E+03"}, 
         {"9.6000E+03", "1.5051E+03"}, 
         {"9.7000E+03", "1.6070E+03"}, 
         {"9.8000E+03", "1.7116E+03"}, 
         {"9.9000E+03", "1.8186E+03"}, 
         {"1.0000E+04", "1.9278E+03"}, 
         {"1.0100E+04", "2.0391E+03"}, 
         {"1.0200E+04", "2.1522E+03"}, 
         {"1.0300E+04", "2.2669E+03"}, 
         {"1.0400E+04", "2.3832E+03"}, 
         {"1.0500E+04", "2.5006E+03"}, 
         {"1.0600E+04", "2.6191E+03"}, 
         {"1.0700E+04", "2.7386E+03"}, 
         {"1.0800E+04", "2.8589E+03"}, 
         {"1.0900E+04", "2.9798E+03"}, 
         {"1.1000E+04", "3.1011E+03"}, 
         {"1.1100E+04", "3.2228E+03"}, 
         {"1.1200E+04", "3.3448E+03"}, 
         {"1.1300E+04", "3.4669E+03"}, 
         {"1.1400E+04", "3.5889E+03"}, 
         {"1.1500E+04", "3.7109E+03"}, 
         {"1.1600E+04", "3.8327E+03"}, 
         {"1.1700E+04", "3.9542E+03"}, 
         {"1.1800E+04", "4.0757E+03"}, 
         {"1.1900E+04", "4.1966E+03"}, 
         {"1.2000E+04", "4.3170E+03"}, 
         {"1.2100E+04", "4.4370E+03"}, 
         {"1.2200E+04", "4.5563E+03"}, 
         {"1.2400E+04", "4.7937E+03"}, 
         {"1.2500E+04", "4.9113E+03"}, 
         {"1.2600E+04", "5.0281E+03"}, 
         {"1.2700E+04", "5.1442E+03"}, 
         {"1.2800E+04", "5.2595E+03"}, 
         {"1.2900E+04", "5.3741E+03"}, 
         {"1.3000E+04", "5.4878E+03"}, 
         {"1.3100E+04", "5.6008E+03"}, 
         {"1.3300E+04", "5.8248E+03"}, 
         {"1.3400E+04", "5.9351E+03"}, 
         {"1.3500E+04", "6.0446E+03"}, 
         {"1.3600E+04", "6.1531E+03"}, 
         {"1.3700E+04", "6.2607E+03"}, 
         {"1.3800E+04", "6.3673E+03"}, 
         {"1.3900E+04", "6.4730E+03"}, 
         {"1.4000E+04", "6.5777E+03"}, 
         {"1.4100E+04", "6.6814E+03"}, 
         {"1.4200E+04", "6.7841E+03"}, 
         {"1.4300E+04", "6.8858E+03"}, 
         {"1.4400E+04", "6.9865E+03"}, 
         {"1.4500E+04", "7.0862E+03"}, 
         {"1.4600E+04", "7.1849E+03"}, 
         {"1.4700E+04", "7.2826E+03"}, 
         {"1.4800E+04", "7.3792E+03"}, 
         {"1.4900E+04", "7.4749E+03"}, 
         {"1.5000E+04", "7.5715E+03"}, 
         {"1.5100E+04", "7.6652E+03"}, 
         {"1.5200E+04", "7.7579E+03"}, 
         {"1.5300E+04", "7.8497E+03"}, 
         {"1.5400E+04", "7.9405E+03"}, 
         {"1.5500E+04", "8.0303E+03"}, 
         {"1.5600E+04", "8.1192E+03"}, 
         {"1.5700E+04", "8.2071E+03"}, 
         {"1.5800E+04", "8.2942E+03"}, 
         {"1.5900E+04", "8.3803E+03"}, 
         {"1.6000E+04", "8.4656E+03"}, 
         {"1.6100E+04", "8.5500E+03"}, 
         {"1.6200E+04", "8.6336E+03"}, 
         {"1.6300E+04", "8.7164E+03"}, 
         {"1.6400E+04", "8.7984E+03"}, 
         {"1.6500E+04", "8.8797E+03"}, 
         {"1.6600E+04", "8.9602E+03"}, 
         {"1.6700E+04", "9.0400E+03"}, 
         {"1.6800E+04", "9.1192E+03"}, 
         {"1.6900E+04", "9.1977E+03"}, 
         {"1.7000E+04", "9.2756E+03"}, 
         {"1.7100E+04", "9.3529E+03"}, 
         {"1.7200E+04", "9.4297E+03"}, 
         {"1.7300E+04", "9.5059E+03"}, 
         {"1.7400E+04", "9.5816E+03"}, 
         {"1.7500E+04", "9.6568E+03"}, 
         {"1.7600E+04", "9.7316E+03"}, 
         {"1.7700E+04", "9.8059E+03"}, 
         {"1.7800E+04", "9.8798E+03"}, 
         {"1.7900E+04", "9.9534E+03"}, 
         {"1.8000E+04", "1.0027E+04"}, 
         {"1.8100E+04", "1.0099E+04"}, 
         {"1.8200E+04", "1.0168E+04"}, 
         {"1.8300E+04", "1.0241E+04"}, 
         {"1.8400E+04", "1.0313E+04"}, 
         {"1.8500E+04", "1.0384E+04"}, 
         {"1.8600E+04", "1.0456E+04"}, 
         {"1.8700E+04", "1.0527E+04"}, 
         {"1.8800E+04", "1.0598E+04"}, 
         {"1.8900E+04", "1.0669E+04"}, 
         {"1.9000E+04", "1.0740E+04"}, 
         {"1.9100E+04", "1.0811E+04"}, 
         {"1.9200E+04", "1.0881E+04"}, 
         {"1.9300E+04", "1.0951E+04"}, 
         {"1.9400E+04", "1.1022E+04"}, 
         {"1.9500E+04", "1.1092E+04"}, 
         {"1.9600E+04", "1.1162E+04"}, 
         {"1.9700E+04", "1.1232E+04"}, 
         {"1.9800E+04", "1.1302E+04"}, 
         {"1.9900E+04", "1.1372E+04"}, 
         {"2.0000E+04", "1.1442E+04"}, 
         {"2.0100E+04", "1.1512E+04"}, 
         {"2.0200E+04", "1.1582E+04"}, 
         {"2.0300E+04", "1.1652E+04"}, 
         {"2.0400E+04", "1.1721E+04"}, 
         {"2.0500E+04", "1.1791E+04"}, 
         {"2.0600E+04", "1.1861E+04"}, 
         {"2.0700E+04", "1.1931E+04"}, 
         {"2.0800E+04", "1.2001E+04"}, 
         {"2.0900E+04", "1.2071E+04"}, 
         {"2.1000E+04", "1.2142E+04"}, 
         {"2.1100E+04", "1.2212E+04"}, 
         {"2.1200E+04", "1.2282E+04"}, 
         {"2.1300E+04", "1.2353E+04"}, 
         {"2.1400E+04", "1.2423E+04"}, 
         {"2.1500E+04", "1.2494E+04"}, 
         {"2.1600E+04", "1.2564E+04"}, 
         {"2.1700E+04", "1.2635E+04"}, 
         {"2.1800E+04", "1.2706E+04"}, 
         {"2.1900E+04", "1.2777E+04"}, 
         {"2.2000E+04", "1.2849E+04"}, 
         {"2.2100E+04", "1.2924E+04"}, 
         {"2.2200E+04", "1.2996E+04"}, 
         {"2.2300E+04", "1.3068E+04"}, 
         {"2.2400E+04", "1.3141E+04"}, 
         {"2.2500E+04", "1.3214E+04"}, 
         {"2.2600E+04", "1.3287E+04"}, 
         {"2.2700E+04", "1.3360E+04"}, 
         {"2.2800E+04", "1.3433E+04"}, 
         {"2.2900E+04", "1.3507E+04"}, 
         {"2.3000E+04", "1.3581E+04"}, 
         {"2.3100E+04", "1.3656E+04"}, 
         {"2.3200E+04", "1.3730E+04"}, 
         {"2.3300E+04", "1.3805E+04"}, 
         {"2.3400E+04", "1.3881E+04"}, 
         {"2.3500E+04", "1.3956E+04"}, 
         {"2.3600E+04", "1.4032E+04"}, 
         {"2.3700E+04", "1.4109E+04"}, 
         {"2.3800E+04", "1.4186E+04"}, 
         {"2.3900E+04", "1.4263E+04"}, 
         {"2.4000E+04", "1.4340E+04"}});
    model.component("comp1").material("mat1").propertyGroup("def").func("int5").set("interp", "piecewisecubic");
    model.component("comp1").material("mat1").propertyGroup("def").func("int5").set("extrap", "linear");
    model.component("comp1").material("mat1").propertyGroup("def").func("int5").set("fununit", new String[]{"S/m"});
    model.component("comp1").material("mat1").propertyGroup("def").func("int5").set("argunit", new String[]{"K"});
    model.component("comp1").material("mat1").propertyGroup("def").set("density", "rho(T)");
    model.component("comp1").material("mat1").propertyGroup("def").set("heatcapacity", "cp(T)");
    model.component("comp1").material("mat1").propertyGroup("def")
         .set("thermalconductivity", new String[]{"k(T)", "0", "0", "0", "k(T)", "0", "0", "0", "k(T)"});
    model.component("comp1").material("mat1").propertyGroup("def")
         .set("relpermeability", new String[]{"1", "0", "0", "0", "1", "0", "0", "0", "1"});
    model.component("comp1").material("mat1").propertyGroup("def")
         .set("relpermittivity", new String[]{"1", "0", "0", "0", "1", "0", "0", "0", "1"});
    model.component("comp1").material("mat1").propertyGroup("def").set("dynamicviscosity", "mu(T)");
    model.component("comp1").material("mat1").propertyGroup("def")
         .set("electricconductivity", new String[]{"if(sigma(T)<sigma_min,sigma_min,sigma(T))", "0", "0", "0", "if(sigma(T)<sigma_min,sigma_min,sigma(T))", "0", "0", "0", "if(sigma(T)<sigma_min,sigma_min,sigma(T))"});
    model.component("comp1").material("mat1").propertyGroup("def").set("ratioofspecificheat", "1.41");
    model.component("comp1").material("mat1").propertyGroup("def").set("sigma_min", "1[S/m]");
    model.component("comp1").material("mat1").propertyGroup("def").descr("sigma_min", "");
    model.component("comp1").material("mat1").propertyGroup("def").addInput("temperature");
    model.component("comp1").material("mat1").propertyGroup("RadiationHeatTransfer").func("int1")
         .set("funcname", "Qrad");

    return model;
  }

  public static Model run3(Model model) {
    model.component("comp1").material("mat1").propertyGroup("RadiationHeatTransfer").func("int1")
         .set("table", new String[][]{{"0", "0"}, 
         {"5.0232E+03", "3.7318E+05"}, 
         {"5.1444E+03", "4.3193E+05"}, 
         {"5.2018E+03", "5.2879E+05"}, 
         {"5.3478E+03", "7.9308E+05"}, 
         {"5.4336E+03", "1.0898E+06"}, 
         {"5.4882E+03", "1.4967E+06"}, 
         {"5.5740E+03", "2.0568E+06"}, 
         {"5.6597E+03", "2.8264E+06"}, 
         {"5.7455E+03", "3.8840E+06"}, 
         {"5.8610E+03", "5.6566E+06"}, 
         {"5.9475E+03", "7.5531E+06"}, 
         {"6.0014E+03", "1.0675E+07"}, 
         {"6.1488E+03", "1.5116E+07"}, 
         {"6.2672E+03", "1.9626E+07"}, 
         {"6.3841E+03", "2.6987E+07"}, 
         {"6.5315E+03", "3.8216E+07"}, 
         {"6.6180E+03", "5.1029E+07"}, 
         {"6.7030E+03", "7.2167E+07"}, 
         {"6.8518E+03", "9.6488E+07"}, 
         {"6.9383E+03", "1.2884E+08"}, 
         {"7.0864E+03", "1.7728E+08"}, 
         {"7.2649E+03", "2.5120E+08"}, 
         {"7.4137E+03", "3.3586E+08"}, 
         {"7.5314E+03", "4.4876E+08"}, 
         {"7.7113E+03", "6.0038E+08"}, 
         {"7.8594E+03", "8.2610E+08"}, 
         {"8.0075E+03", "1.1367E+09"}, 
         {"8.1881E+03", "1.4777E+09"}, 
         {"8.3674E+03", "2.0346E+09"}, 
         {"8.5799E+03", "2.5717E+09"}, 
         {"8.7591E+03", "3.5409E+09"}, 
         {"8.9079E+03", "4.7342E+09"}, 
         {"9.1509E+03", "6.1623E+09"}, 
         {"9.3931E+03", "8.2550E+09"}, 
         {"9.5745E+03", "1.0428E+10"}, 
         {"9.7856E+03", "1.3960E+10"}, 
         {"1.0029E+04", "1.7657E+10"}, 
         {"1.0273E+04", "2.2332E+10"}, 
         {"1.0516E+04", "2.9070E+10"}, 
         {"1.0760E+04", "3.5727E+10"}, 
         {"1.1035E+04", "4.5217E+10"}, 
         {"1.1281E+04", "5.2469E+10"}, 
         {"1.1556E+04", "6.4527E+10"}, 
         {"1.1894E+04", "7.9458E+10"}, 
         {"1.2139E+04", "9.7654E+10"}, 
         {"1.2447E+04", "1.1025E+11"}, 
         {"1.2755E+04", "1.3183E+11"}, 
         {"1.3095E+04", "1.4894E+11"}, 
         {"1.3434E+04", "1.6826E+11"}, 
         {"1.3775E+04", "1.8470E+11"}, 
         {"1.4116E+04", "2.0275E+11"}, 
         {"1.4457E+04", "2.1627E+11"}, 
         {"1.4798E+04", "2.3069E+11"}, 
         {"1.5171E+04", "2.4622E+11"}, 
         {"1.5545E+04", "2.4311E+11"}, 
         {"1.5888E+04", "2.4283E+11"}, 
         {"1.6232E+04", "2.3090E+11"}, 
         {"1.6607E+04", "2.2611E+11"}, 
         {"1.6982E+04", "2.1514E+11"}, 
         {"1.7327E+04", "1.9879E+11"}, 
         {"1.7670E+04", "1.9453E+11"}, 
         {"1.8046E+04", "1.8510E+11"}, 
         {"1.8390E+04", "1.7601E+11"}, 
         {"1.8766E+04", "1.6273E+11"}, 
         {"1.9141E+04", "1.5484E+11"}, 
         {"1.9487E+04", "1.3902E+11"}, 
         {"1.9831E+04", "1.3219E+11"}, 
         {"2.0175E+04", "1.2214E+11"}, 
         {"2.0521E+04", "1.0966E+11"}, 
         {"2.0864E+04", "1.0731E+11"}, 
         {"2.1209E+04", "1.0204E+11"}, 
         {"2.1584E+04", "9.4347E+10"}, 
         {"2.1960E+04", "8.7230E+10"}, 
         {"2.2304E+04", "8.5363E+10"}, 
         {"2.2618E+04", "7.6591E+10"}, 
         {"2.2962E+04", "7.2830E+10"}, 
         {"2.3369E+04", "6.9343E+10"}, 
         {"2.3714E+04", "6.4071E+10"}, 
         {"2.4058E+04", "6.0925E+10"}, 
         {"2.4433E+04", "5.7970E+10"}, 
         {"2.4777E+04", "5.5124E+10"}, 
         {"2.5152E+04", "5.2451E+10"}, 
         {"2.5466E+04", "4.8432E+10"}, 
         {"2.5810E+04", "4.6053E+10"}, 
         {"2.6186E+04", "4.2580E+10"}, 
         {"2.6529E+04", "4.2883E+10"}, 
         {"2.6874E+04", "3.9622E+10"}, 
         {"2.7249E+04", "3.7701E+10"}, 
         {"2.7593E+04", "3.5850E+10"}, 
         {"2.7968E+04", "3.4111E+10"}, 
         {"2.8344E+04", "3.2457E+10"}, 
         {"2.8657E+04", "3.0843E+10"}, 
         {"2.9001E+04", "2.9329E+10"}, 
         {"2.9376E+04", "2.7907E+10"}, 
         {"2.9627E+04", "2.5735E+10"}, 
         {"2.9940E+04", "2.5168E+10"}});
    model.component("comp1").material("mat1").propertyGroup("RadiationHeatTransfer").func("int1")
         .set("interp", "piecewisecubic");
    model.component("comp1").material("mat1").propertyGroup("RadiationHeatTransfer").func("int1")
         .set("extrap", "linear");
    model.component("comp1").material("mat1").propertyGroup("RadiationHeatTransfer").func("int1")
         .set("fununit", new String[]{"W/m^3"});
    model.component("comp1").material("mat1").propertyGroup("RadiationHeatTransfer").func("int1")
         .set("argunit", new String[]{"K"});
    model.component("comp1").material("mat1").propertyGroup("RadiationHeatTransfer").set("Qrad", "Qrad(T)");
    model.component("comp1").material("mat1").propertyGroup("RadiationHeatTransfer").addInput("temperature");
    model.component("comp1").material("mat2").label("Tin [liquid,tested at 260 \u00b0C (533 K)]");
    model.component("comp1").material("mat2").set("family", "custom");
    model.component("comp1").material("mat2").set("customspecular", new double[]{0.7843137254901961, 1, 1});
    model.component("comp1").material("mat2").set("fresnel", 0.9);
    model.component("comp1").material("mat2").set("roughness", 0.1);
    model.component("comp1").material("mat2").set("diffusewrap", 0);
    model.component("comp1").material("mat2").set("reflectance", 0);
    model.component("comp1").material("mat2").set("info", new String[][]{{"UNS", "", "L13008"}});
    model.component("comp1").material("mat2").propertyGroup("def").func("k_liquid_2").label("Piecewise 1");
    model.component("comp1").material("mat2").propertyGroup("def").func("k_liquid_2").set("arg", "T");
    model.component("comp1").material("mat2").propertyGroup("def").func("k_liquid_2")
         .set("pieces", new String[][]{{"505.0", "1500.0", "11.43428+0.03384702*T^1-5.119712E-6*T^2"}});
    model.component("comp1").material("mat2").propertyGroup("def").func("k_liquid_2").set("argunit", "K");
    model.component("comp1").material("mat2").propertyGroup("def").func("k_liquid_2").set("fununit", "W/(m*K)");
    model.component("comp1").material("mat2").propertyGroup("def").func("res_liquid_2").label("Piecewise 1.1");
    model.component("comp1").material("mat2").propertyGroup("def").func("res_liquid_2").set("arg", "T");
    model.component("comp1").material("mat2").propertyGroup("def").func("res_liquid_2")
         .set("pieces", new String[][]{{"508.0", "1500.0", "3.88272266E-7+1.03651334E-10*T^1+1.43996249E-13*T^2-8.82256488E-17*T^3+5.32284628E-20*T^4"}});
    model.component("comp1").material("mat2").propertyGroup("def").func("res_liquid_2").set("argunit", "K");
    model.component("comp1").material("mat2").propertyGroup("def").func("res_liquid_2").set("fununit", "ohm*m");
    model.component("comp1").material("mat2").propertyGroup("def").func("alpha_liquid_4").label("Piecewise 2");
    model.component("comp1").material("mat2").propertyGroup("def").func("alpha_liquid_4").set("arg", "T");
    model.component("comp1").material("mat2").propertyGroup("def").func("alpha_liquid_4")
         .set("pieces", new String[][]{{"505.4", "1400.0", "2.996454E-5+1.185385E-8*T^1+8.872342E-16*T^2"}});
    model.component("comp1").material("mat2").propertyGroup("def").func("alpha_liquid_4").set("argunit", "K");
    model.component("comp1").material("mat2").propertyGroup("def").func("alpha_liquid_4").set("fununit", "1/K");
    model.component("comp1").material("mat2").propertyGroup("def").func("C_liquid_2").label("Piecewise 3.1");
    model.component("comp1").material("mat2").propertyGroup("def").func("C_liquid_2").set("arg", "T");
    model.component("comp1").material("mat2").propertyGroup("def").func("C_liquid_2")
         .set("pieces", new String[][]{{"505.0", "1200.0", "436.150829-0.878903224*T^1+0.00157873624*T^2-1.45404436E-6*T^3+6.830017E-10*T^4-1.29500364E-13*T^5"}, {"1200.0", "4700.0", "242.084329-0.0240245676*T^1+2.35368191E-5*T^2-7.55489332E-9*T^3+1.14279023E-12*T^4-6.84133601E-17*T^5"}});
    model.component("comp1").material("mat2").propertyGroup("def").func("C_liquid_2").set("argunit", "K");
    model.component("comp1").material("mat2").propertyGroup("def").func("C_liquid_2").set("fununit", "J/(kg*K)");
    model.component("comp1").material("mat2").propertyGroup("def").func("sigma_liquid_2").label("Piecewise 4");
    model.component("comp1").material("mat2").propertyGroup("def").func("sigma_liquid_2").set("arg", "T");
    model.component("comp1").material("mat2").propertyGroup("def").func("sigma_liquid_2")
         .set("pieces", new String[][]{{"508.0", "1500.0", "1/(5.32284628E-20*T^4-8.82256488E-17*T^3+1.43996249E-13*T^2+1.03651334E-10*T+3.88272266E-07)"}});
    model.component("comp1").material("mat2").propertyGroup("def").func("sigma_liquid_2").set("argunit", "K");
    model.component("comp1").material("mat2").propertyGroup("def").func("sigma_liquid_2").set("fununit", "S/m");
    model.component("comp1").material("mat2").propertyGroup("def").func("HC_liquid_2").label("Piecewise 5.1");
    model.component("comp1").material("mat2").propertyGroup("def").func("HC_liquid_2").set("arg", "T");
    model.component("comp1").material("mat2").propertyGroup("def").func("HC_liquid_2")
         .set("pieces", new String[][]{{"505.0", "1200.0", "51.7667417-0.104317024*T^1+1.87380204E-4*T^2-1.72580525E-7*T^3+8.1065472E-11*T^4-1.53703982E-14*T^5"}, {"1200.0", "4700.0", "28.7329896-0.00285147593*T^1+2.79358506E-6*T^2-8.96690286E-10*T^3+1.35637773E-13*T^4-8.11998168E-18*T^5"}});
    model.component("comp1").material("mat2").propertyGroup("def").func("HC_liquid_2").set("argunit", "K");
    model.component("comp1").material("mat2").propertyGroup("def").func("HC_liquid_2").set("fununit", "J/(mol*K)");
    model.component("comp1").material("mat2").propertyGroup("def").func("VP_liquid_2").label("Piecewise 6");
    model.component("comp1").material("mat2").propertyGroup("def").func("VP_liquid_2").set("arg", "T");
    model.component("comp1").material("mat2").propertyGroup("def").func("VP_liquid_2")
         .set("pieces", new String[][]{{"505.0", "1850.0", "(exp((-1.53320000e+04/T+8.14281000e+00)*log(10.0)))*1.33320000e+02"}});
    model.component("comp1").material("mat2").propertyGroup("def").func("VP_liquid_2").set("argunit", "K");
    model.component("comp1").material("mat2").propertyGroup("def").func("VP_liquid_2").set("fununit", "Pa");
    model.component("comp1").material("mat2").propertyGroup("def").func("rho_liquid_2").label("Piecewise 7");
    model.component("comp1").material("mat2").propertyGroup("def").func("rho_liquid_2").set("arg", "T");
    model.component("comp1").material("mat2").propertyGroup("def").func("rho_liquid_2")
         .set("pieces", new String[][]{{"505.0", "1400.0", "7319.324-0.6191594*T^1-1.473564E-4*T^2"}});
    model.component("comp1").material("mat2").propertyGroup("def").func("rho_liquid_2").set("argunit", "K");
    model.component("comp1").material("mat2").propertyGroup("def").func("rho_liquid_2").set("fununit", "kg/m^3");
    model.component("comp1").material("mat2").propertyGroup("def").func("TD_liquid_2").label("Piecewise 8");
    model.component("comp1").material("mat2").propertyGroup("def").func("TD_liquid_2").set("arg", "T");
    model.component("comp1").material("mat2").propertyGroup("def").func("TD_liquid_2")
         .set("pieces", new String[][]{{"505.0", "1400.0", "3.40624389E-7+3.96475342E-8*T^1-2.33853054E-11*T^2+1.18077932E-14*T^3-2.38040692E-18*T^4"}});
    model.component("comp1").material("mat2").propertyGroup("def").func("TD_liquid_2").set("argunit", "K");
    model.component("comp1").material("mat2").propertyGroup("def").func("TD_liquid_2").set("fununit", "m^2/s");
    model.component("comp1").material("mat2").propertyGroup("def").func("eta").label("Piecewise 9");
    model.component("comp1").material("mat2").propertyGroup("def").func("eta").set("arg", "T");
    model.component("comp1").material("mat2").propertyGroup("def").func("eta")
         .set("pieces", new String[][]{{"495.0", "1020.0", "exp(6.17825053E+02/T - 7.48221866E+00)"}});
    model.component("comp1").material("mat2").propertyGroup("def").func("eta").set("argunit", "K");
    model.component("comp1").material("mat2").propertyGroup("def").func("eta").set("fununit", "Pa*s");
    model.component("comp1").material("mat2").propertyGroup("def").func("app_eta").label("Piecewise 10 ");
    model.component("comp1").material("mat2").propertyGroup("def").func("app_eta").set("arg", "T");
    model.component("comp1").material("mat2").propertyGroup("def").func("app_eta").set("smooth", "contd2");
    model.component("comp1").material("mat2").propertyGroup("def").func("app_eta")
         .set("pieces", new String[][]{{"0", "505", "1e6[Pa*s]"}, {"505", "2500", "0.00423*exp(842/T[K])   [Pa*s]"}});
    model.component("comp1").material("mat2").propertyGroup("def").func("app_eta").set("fununit", "Pa*s");
    model.component("comp1").material("mat2").propertyGroup("def").func("SurfF").label("Piecewise 11");
    model.component("comp1").material("mat2").propertyGroup("def").func("SurfF").set("arg", "T");
    model.component("comp1").material("mat2").propertyGroup("def").func("SurfF")
         .set("pieces", new String[][]{{"537.0", "1185.0", "0.588817-8.10394E-5*T^1"}});
    model.component("comp1").material("mat2").propertyGroup("def").func("SurfF").set("argunit", "K");
    model.component("comp1").material("mat2").propertyGroup("def").func("SurfF").set("fununit", "N/m");
    model.component("comp1").material("mat2").propertyGroup("def")
         .set("thermalconductivity", new String[]{"k_liquid_2(T)", "0", "0", "0", "k_liquid_2(T)", "0", "0", "0", "k_liquid_2(T)"});
    model.component("comp1").material("mat2").propertyGroup("def")
         .set("INFO_PREFIX:thermalconductivity", "Reference: W. Hemminger, High Temperatures-High Pressures, v17, p465 (1985) and C.Y. Ho, R.W. Powell, and P.E. Liley, Journal of Physical and Chemical Reference Data, v1, No. 2, p279 (1972) https://srd.nist.gov/JPCRD/jpcrd7.pdf\nNote: Tmp near 232 \u00b0C (505 K), error is 5% to 15%");
    model.component("comp1").material("mat2").propertyGroup("def")
         .set("resistivity", new String[]{"res_liquid_2(T)", "0", "0", "0", "res_liquid_2(T)", "0", "0", "0", "res_liquid_2(T)"});
    model.component("comp1").material("mat2").propertyGroup("def")
         .set("INFO_PREFIX:resistivity", "Reference: Y. Plevachuk, S. Mudry, V. Sklyarchuk, A. Yakymovych, U.E. Klotz, and M. Roth, Journal of Materials Science, v42, No. 20, p8618 (2007) https://doi.org/10.1007/s10853-007-1821-5\nNote: Tmp near 232 \u00b0C (505 K), 4-point technique");
    model.component("comp1").material("mat2").propertyGroup("def")
         .set("thermalexpansioncoefficient", new String[]{"(alpha_liquid_4(T)+(Tempref-505[K])*if(abs(T-Tempref)>1e-3,(alpha_liquid_4(T)-alpha_liquid_4(Tempref))/(T-Tempref),d(alpha_liquid_4(T),T)))/(1+alpha_liquid_4(Tempref)*(Tempref-505[K]))", "0", "0", "0", "(alpha_liquid_4(T)+(Tempref-505[K])*if(abs(T-Tempref)>1e-3,(alpha_liquid_4(T)-alpha_liquid_4(Tempref))/(T-Tempref),d(alpha_liquid_4(T),T)))/(1+alpha_liquid_4(Tempref)*(Tempref-505[K]))", "0", "0", "0", "(alpha_liquid_4(T)+(Tempref-505[K])*if(abs(T-Tempref)>1e-3,(alpha_liquid_4(T)-alpha_liquid_4(Tempref))/(T-Tempref),d(alpha_liquid_4(T),T)))/(1+alpha_liquid_4(Tempref)*(Tempref-505[K]))"});
    model.component("comp1").material("mat2").propertyGroup("def")
         .set("INFO_PREFIX:thermalexpansioncoefficient", "Reference: W.D. Drotning, High Temperature Science, v11, p265 (1979)\nNote: the reference temperature is 232 \u00b0C (505 K), Tmp near 232 \u00b0C (505 K), calculated from the density\nReference temperature: 505.40[K]");
    model.component("comp1").material("mat2").propertyGroup("def").set("heatcapacity", "C_liquid_2(T)");
    model.component("comp1").material("mat2").propertyGroup("def")
         .set("INFO_PREFIX:heatcapacity", "Reference: B.J. McBride, S. Gordon, and M.A. Reno, Thermodynamic Data for Fifty Reference Elements, NASA Technical Paper 3287 (1993) https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/20010021116.pdf\nNote: Tmp near 232 \u00b0C (505 K)");
    model.component("comp1").material("mat2").propertyGroup("def")
         .set("electricconductivity", new String[]{"sigma_liquid_2(T)", "0", "0", "0", "sigma_liquid_2(T)", "0", "0", "0", "sigma_liquid_2(T)"});
    model.component("comp1").material("mat2").propertyGroup("def")
         .set("INFO_PREFIX:electricconductivity", "Reference: Y. Plevachuk, S. Mudry, V. Sklyarchuk, A. Yakymovych, U.E. Klotz, and M. Roth, Journal of Materials Science, v42, No. 20, p8618 (2007) https://doi.org/10.1007/s10853-007-1821-5\nNote: Tmp near 232 \u00b0C (505 K), 4-point technique, calculated as the reciprocal of the resistivity");
    model.component("comp1").material("mat2").propertyGroup("def").set("HC", "HC_liquid_2(T)");
    model.component("comp1").material("mat2").propertyGroup("def")
         .set("INFO_PREFIX:HC", "Reference: B.J. McBride, S. Gordon, and M.A. Reno, Thermodynamic Data for Fifty Reference Elements, NASA Technical Paper 3287 (1993) https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/20010021116.pdf\nNote: Tmp near 232 \u00b0C (505 K)");
    model.component("comp1").material("mat2").propertyGroup("def").set("VP", "VP_liquid_2(T)");
    model.component("comp1").material("mat2").propertyGroup("def")
         .set("INFO_PREFIX:VP", "Reference: C.B. Alcock, V.P. Itkin, and M.K. Horrigan, Canadian Metallurgical Quarterly, v23, No. 3, p309 (1984) https://doi.org/10.1179/cmq.1984.23.3.309\nNote: Tmp near 232 \u00b0C (505 K), 5% error or less");
    model.component("comp1").material("mat2").propertyGroup("def").set("density", "rho_liquid_2(T)");
    model.component("comp1").material("mat2").propertyGroup("def")
         .set("INFO_PREFIX:density", "Reference: W.D. Drotning, High Temperature Science, v11, p265 (1979)\nNote: Tmp near 232 \u00b0C (505 K)");
    model.component("comp1").material("mat2").propertyGroup("def").set("TD", "TD_liquid_2(T)");
    model.component("comp1").material("mat2").propertyGroup("def")
         .set("INFO_PREFIX:TD", "Reference: B.J. McBride, S. Gordon, and M.A. Reno, Thermodynamic Data for Fifty Reference Elements, NASA Technical Paper 3287 (1993) https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/20010021116.pdf and W. Hemminger, High Temperatures-High Pressures, v17, p465 (1985) and C.Y. Ho, R.W. Powell, and P.E. Liley, Journal of Physical and Chemical Reference Data, v1, No. 2, p279 (1972) https://srd.nist.gov/JPCRD/jpcrd7.pdf\nNote: Tmp near 232 \u00b0C (505 K), calculated from the thermal conductivity, density, and specific heat");
    model.component("comp1").material("mat2").propertyGroup("def").set("dynamicviscosity", "eta(T)");
    model.component("comp1").material("mat2").propertyGroup("def")
         .set("INFO_PREFIX:dynamicviscosity", "Reference: H.R. Thresh and A.F. Crawley, Metallurgical Transactions, v1, No. 6, p1531 (1970) https://doi.org/10.1007/BF02641997 and W.-K. Rhim, K. Ohsaka, P.-F. Paradis, and R.E. Spjut, Review of Scientific Instruments, v70, No. 6, p2796 (1999) https://doi.org/10.1063/1.1149797 and Y. Plevachuk, V. Sklyarchuk, W. Hoyer, and I. Kaban, Journal of Materials Science, v41, No. 14, p4632 (2006) https://doi.org/10.1007/s10853-006-0053-4 and H.J. Fisher and A. Phillips, Journal of Metals, v6, No. 9, p1060 (1954) https://doi.org/10.1007/BF03398346\nNote: Tmp near 232 \u00b0C (505 K)");
    model.component("comp1").material("mat2").propertyGroup("def").set("app_eta", "app_eta(S[s])");
    model.component("comp1").material("mat2").propertyGroup("def")
         .set("INFO_PREFIX:app_eta", "Reference: V. Vijay and Z. Fan, in Frontiers in Solidification Science, Edited by J. Hoyt, M. Plapp, G. Faivre, S. Liu, published by The Minerals, Metals and Materials Society (TMS) (2007)\nNote: tested at 260 \u00b0C (533 K), Tmp near 232 \u00b0C (505 K), Searle type concentric cylinder viscometer, value at 0 shear rate is from the viscosity data\nReference temperature: 533.15[K]");
    model.component("comp1").material("mat2").propertyGroup("def").set("S", "");
    model.component("comp1").material("mat2").propertyGroup("def").set("SurfF", "SurfF(T)");
    model.component("comp1").material("mat2").propertyGroup("def")
         .set("INFO_PREFIX:SurfF", "Reference: W. Gasior, Z. Moser, and J. Pstrus, Journal of Phase Equilibria, v22, No. 1, p20 (2001) https://doi.org/10.1361/105497101770339256 and A. Kashezhev, V. Kumykov, R. Kutuev, M. Ponezhev, V. Sozaev, and A.Kh. Shermetov, Bulletin of the Russian Academy of Sciences: Physics, v80, No. 6, p746 (2016) https://doi.org/10.3103/S1062873816060150\nNote: Tmp near 232 \u00b0C (505 K), measured in an inert atmosphere");
    model.component("comp1").material("mat2").propertyGroup("def").addInput("temperature");
    model.component("comp1").material("mat2").propertyGroup("def").addInput("strainreferencetemperature");
    model.component("comp1").material("mat2").propertyGroup("ThermalExpansion").func("dL_liquid_4")
         .label("Piecewise");
    model.component("comp1").material("mat2").propertyGroup("ThermalExpansion").func("dL_liquid_4").set("arg", "T");
    model.component("comp1").material("mat2").propertyGroup("ThermalExpansion").func("dL_liquid_4")
         .set("pieces", new String[][]{{"505.4", "1400.0", "-0.0151459793+2.397641E-5*T^1+1.185574E-8*T^2"}});
    model.component("comp1").material("mat2").propertyGroup("ThermalExpansion").func("dL_liquid_4")
         .set("argunit", "K");
    model.component("comp1").material("mat2").propertyGroup("ThermalExpansion")
         .set("dL", new String[]{"(dL_liquid_4(T)-dL_liquid_4(Tempref))/(1+dL_liquid_4(Tempref))", "0", "0", "0", "(dL_liquid_4(T)-dL_liquid_4(Tempref))/(1+dL_liquid_4(Tempref))", "0", "0", "0", "(dL_liquid_4(T)-dL_liquid_4(Tempref))/(1+dL_liquid_4(Tempref))"});
    model.component("comp1").material("mat2").propertyGroup("ThermalExpansion")
         .set("INFO_PREFIX:dL", "Reference: W.D. Drotning, High Temperature Science, v11, p265 (1979)\nNote: the reference temperature is 232 \u00b0C (505 K), Tmp near 232 \u00b0C (505 K), calculated from the density\nReference temperature: 505.40[K]");
    model.component("comp1").material("mat2").propertyGroup("ThermalExpansion").addInput("temperature");
    model.component("comp1").material("mat2").propertyGroup("ThermalExpansion")
         .addInput("strainreferencetemperature");

    model.component("comp1").common("free1").set("stiffeningFactor", "S");
    model.component("comp1").common("disp2").set("prescribedMeshVelocity", new String[]{"-v_n*nx", "-v_n*ny", "0"});

    model.component("comp1").physics("ht").prop("PhysicalModelProperty").set("Tref", "T_amb");
    model.component("comp1").physics("ht").feature("init1").set("Tinit", "T_amb");
    model.component("comp1").physics("ht").feature("bhs1").set("Qb_input", "q_laser - Lv_sn*J_evap");
    model.component("comp1").physics("ht2").prop("PhysicalModelProperty").set("Tref", "T_amb");
    model.component("comp1").physics("ht2").feature("fluid1").set("minput_strainreferencetemperature", "T_amb");
    model.component("comp1").physics("ht2").feature("init1").set("Tinit", "T_amb");
    model.component("comp1").physics("ht2").feature("bhs1").set("Qb_input", "Lv_sn*J_evap");
    model.component("comp1").physics("spf").prop("PhysicalModelProperty").set("pref", "P_amb");
    model.component("comp1").physics("spf").feature("fp1").set("minput_strainreferencetemperature", "T_amb");
    model.component("comp1").physics("spf").feature("wallbc1").set("BoundaryCondition", "Slip");
    model.component("comp1").physics("spf").feature("bs1")
         .set("Fbnd", new String[][]{{"-d_sigma_dT*(Ty*nx - Tx*ny)*(-ny)"}, {"-d_sigma_dT*(Ty*nx - Tx*ny)*nx"}, {"0"}});
    model.component("comp1").physics("spf").feature("bs1").label("Boundary Stress 1 Marangoni shear stress");
    model.component("comp1").physics("spf2").prop("PhysicalModelProperty")
         .set("Compressibility", "WeaklyCompressible");
    model.component("comp1").physics("spf2").prop("PhysicalModelProperty").set("pref", "P_amb");
    model.component("comp1").physics("spf2").feature("fp1").set("minput_strainreferencetemperature", "T_amb");
    model.component("comp1").physics("spf2").feature("bs1").set("BoundaryCondition", "NormalStress");
    model.component("comp1").physics("spf2").feature("bs1").set("f0", "-(1+beta_r/2)*Psat");
    model.component("comp1").physics("tds").feature("cdm1").set("u_src", "root.comp1.u2");
    model.component("comp1").physics("tds").feature("cdm1").set("DiffusionMaterialList", "mat1");
    model.component("comp1").physics("tds").feature("cdm1").set("minput_temperature_src", "root.comp1.T2");
    model.component("comp1").physics("tds").feature("fl1").set("IncludeConvection", true);
    model.component("comp1").physics("tds").feature("fl1").set("species", true);
    model.component("comp1").physics("tds").feature("fl1").set("J0", "J_evap / M_sn");
    model.component("comp1").physics("tds").feature("fl1").label("Flux 1 Species concentration");
    model.component("comp1").physics("tds").feature("cdm2").set("u_src", "root.comp1.u2");
    model.component("comp1").physics("tds").feature("cdm2").set("DiffusionMaterialList", "mat1");
    model.component("comp1").physics("tds").feature("cdm2")
         .set("D_c", new String[][]{{"Dm0*(T2/300[K])^1.75 / (nitf2.pA/1[atm])"}, {"0"}, {"0"}, {"0"}, {"Dm0*(T2/300[K])^1.75 / (nitf2.pA/1[atm])"}, {"0"}, {"0"}, {"0"}, {"Dm0*(T2/300[K])^1.75 / (nitf2.pA/1[atm])"}});
    model.component("comp1").physics("tds").feature("cdm2").set("minput_temperature_src", "root.comp1.T2");

    model.component("comp1").multiphysics("nitf1").set("includeKineticEnergy", true);
    model.component("comp1").multiphysics("nitf2").set("includeKineticEnergy", true);
    model.component("comp1").multiphysics("nitf2").set("Fluid_physics", "spf2");
    model.component("comp1").multiphysics("nitf2").set("Heat_physics", "ht2");

    model.component("comp1").mesh("mesh1").feature("size").set("hauto", 4);
    model.component("comp1").mesh("mesh1").feature("size").set("table", "cfd");
    model.component("comp1").mesh("mesh1").feature("ftri2").feature("size1").set("custom", "on");
    model.component("comp1").mesh("mesh1").feature("ftri2").feature("size1").set("hmax", "mesh_size_int");
    model.component("comp1").mesh("mesh1").feature("ftri2").feature("size1").set("hmaxactive", true);
    model.component("comp1").mesh("mesh1").feature("ftri3").feature("size1").set("custom", "on");
    model.component("comp1").mesh("mesh1").feature("ftri3").feature("size1").set("hmax", "mesh_size_ext");
    model.component("comp1").mesh("mesh1").feature("ftri3").feature("size1").set("hmaxactive", true);
    model.component("comp1").mesh("mesh1").run();

    model.component("comp1").probe("dom1").set("table", "tbl1");
    model.component("comp1").probe("dom1").set("window", "window2");

    model.study().create("std1");
    model.study("std1").create("time", "Transient");

    model.sol().create("sol1");
    model.sol("sol1").study("std1");
    model.sol("sol1").attach("std1");
    model.sol("sol1").create("st1", "StudyStep");
    model.sol("sol1").create("v1", "Variables");
    model.sol("sol1").create("t1", "Time");
    model.sol("sol1").feature("t1").create("se1", "Segregated");
    model.sol("sol1").feature("t1").create("d1", "Direct");
    model.sol("sol1").feature("t1").create("d2", "Direct");
    model.sol("sol1").feature("t1").create("d3", "Direct");
    model.sol("sol1").feature("t1").create("d4", "Direct");
    model.sol("sol1").feature("t1").create("d5", "Direct");
    model.sol("sol1").feature("t1").create("i1", "Iterative");
    model.sol("sol1").feature("t1").create("i2", "Iterative");
    model.sol("sol1").feature("t1").create("i3", "Iterative");
    model.sol("sol1").feature("t1").create("i4", "Iterative");
    model.sol("sol1").feature("t1").create("i5", "Iterative");
    model.sol("sol1").feature("t1").feature("se1").create("ss1", "SegregatedStep");
    model.sol("sol1").feature("t1").feature("se1").create("ss2", "SegregatedStep");
    model.sol("sol1").feature("t1").feature("se1").create("ss3", "SegregatedStep");
    model.sol("sol1").feature("t1").feature("se1").create("ss4", "SegregatedStep");
    model.sol("sol1").feature("t1").feature("se1").create("ss5", "SegregatedStep");
    model.sol("sol1").feature("t1").feature("se1").create("ll1", "LowerLimit");
    model.sol("sol1").feature("t1").feature("se1").feature().remove("ssDef");
    model.sol("sol1").feature("t1").feature("i1").create("mg1", "Multigrid");
    model.sol("sol1").feature("t1").feature("i1").feature("mg1").feature("pr").create("sl1", "SORLine");
    model.sol("sol1").feature("t1").feature("i1").feature("mg1").feature("po").create("sl1", "SORLine");
    model.sol("sol1").feature("t1").feature("i1").feature("mg1").feature("cs").create("d1", "Direct");
    model.sol("sol1").feature("t1").feature("i2").create("mg1", "Multigrid");
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("pr").create("sc1", "SCGS");
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("po").create("sc1", "SCGS");
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("cs").create("d1", "Direct");
    model.sol("sol1").feature("t1").feature("i3").create("mg1", "Multigrid");
    model.sol("sol1").feature("t1").feature("i3").feature("mg1").feature("pr").create("so1", "SOR");
    model.sol("sol1").feature("t1").feature("i3").feature("mg1").feature("po").create("so1", "SOR");
    model.sol("sol1").feature("t1").feature("i3").feature("mg1").feature("cs").create("d1", "Direct");
    model.sol("sol1").feature("t1").feature("i4").create("mg1", "Multigrid");
    model.sol("sol1").feature("t1").feature("i4").feature("mg1").feature("pr").create("sc1", "SCGS");
    model.sol("sol1").feature("t1").feature("i4").feature("mg1").feature("po").create("sc1", "SCGS");
    model.sol("sol1").feature("t1").feature("i4").feature("mg1").feature("cs").create("d1", "Direct");
    model.sol("sol1").feature("t1").feature("i5").create("mg1", "Multigrid");
    model.sol("sol1").feature("t1").feature("i5").feature("mg1").feature("pr").create("so1", "SOR");
    model.sol("sol1").feature("t1").feature("i5").feature("mg1").feature("po").create("so1", "SOR");
    model.sol("sol1").feature("t1").feature("i5").feature("mg1").feature("cs").create("d1", "Direct");
    model.sol("sol1").feature("t1").feature().remove("fcDef");

    model.result().dataset().create("dset2", "Solution");
    model.result().dataset().create("avh1", "Average");
    model.result().dataset("dset2").set("probetag", "dom1");
    model.result().dataset("avh1").set("probetag", "dom1");
    model.result().dataset("avh1").set("data", "dset2");
    model.result().dataset("avh1").selection().geom("geom1", 2);
    model.result().dataset("avh1").selection().set(2);
    model.result().numerical().create("int1", "IntLine");
    model.result().numerical().create("int2", "IntSurface");
    model.result().numerical().create("int3", "IntVolume");
    model.result().numerical().create("pev1", "EvalPoint");
    model.result().numerical("pev1").set("probetag", "dom1");
    model.result().create("pg1", "PlotGroup1D");
    model.result().create("pg2", "PlotGroup2D");
    model.result().create("pg3", "PlotGroup2D");
    model.result().create("pg4", "PlotGroup2D");
    model.result().create("pg5", "PlotGroup2D");
    model.result().create("pg6", "PlotGroup2D");
    model.result().create("pg7", "PlotGroup2D");
    model.result().create("pg8", "PlotGroup2D");
    model.result().create("pg9", "PlotGroup2D");
    model.result().create("pg10", "PlotGroup2D");
    model.result().create("pg11", "PlotGroup2D");
    model.result("pg1").set("probetag", "window2_default");
    model.result("pg1").create("tblp1", "Table");
    model.result("pg1").feature("tblp1").set("probetag", "dom1");
    model.result("pg2").create("surf1", "Surface");
    model.result("pg3").create("surf1", "Surface");
    model.result("pg3").feature("surf1").set("expr", "T2");
    model.result("pg4").create("surf1", "Surface");
    model.result("pg4").feature("surf1").set("expr", "spf.U");
    model.result("pg5").create("con1", "Contour");
    model.result("pg5").feature("con1").set("expr", "p");
    model.result("pg6").create("surf1", "Surface");
    model.result("pg6").feature("surf1").set("expr", "spf2.U");

    return model;
  }

  public static Model run4(Model model) {
    model.result("pg7").create("con1", "Contour");
    model.result("pg7").feature("con1").set("expr", "p2");
    model.result("pg8").create("surf1", "Surface");
    model.result("pg8").create("str1", "Streamline");
    model.result("pg8").feature("surf1").set("expr", "c");
    model.result("pg9").create("surf1", "Surface");
    model.result("pg9").create("arws1", "ArrowSurface");
    model.result("pg9").feature("surf1").set("expr", "nitf1.T");
    model.result("pg9").feature("surf1").create("sel1", "Selection");
    model.result("pg9").feature("surf1").feature("sel1").selection().set(2);
    model.result("pg9").feature("arws1").create("col1", "Color");
    model.result("pg9").feature("arws1").create("filt1", "Filter");
    model.result("pg9").feature("arws1").feature("col1").set("expr", "spf.U");
    model.result("pg9").feature("arws1").feature("filt1").set("expr", "spf.U>nitf1.Uave");
    model.result("pg10").create("surf1", "Surface");
    model.result("pg10").create("arws1", "ArrowSurface");
    model.result("pg10").feature("surf1").set("expr", "nitf2.T");
    model.result("pg10").feature("surf1").create("sel1", "Selection");
    model.result("pg10").feature("surf1").feature("sel1").selection().set(1);
    model.result("pg10").feature("arws1").create("col1", "Color");
    model.result("pg10").feature("arws1").create("filt1", "Filter");
    model.result("pg10").feature("arws1").feature("col1").set("expr", "spf2.U");
    model.result("pg10").feature("arws1").feature("filt1").set("expr", "spf2.U>nitf2.Uave");
    model.result("pg11").create("mesh1", "Mesh");
    model.result("pg11").feature("mesh1").create("sel1", "MeshSelection");
    model.result("pg11").feature("mesh1").feature("sel1").selection().set(1, 2);
    model.result().report().create("rpt1", "Report");
    model.result().report("rpt1").create("tp1", "TitlePage");
    model.result().report("rpt1").create("toc1", "TableOfContents");
    model.result().report("rpt1").create("sec1", "Section");
    model.result().report("rpt1").create("sec2", "Section");
    model.result().report("rpt1").create("sec3", "Section");
    model.result().report("rpt1").create("sec4", "Section");
    model.result().report("rpt1").feature("sec1").create("root1", "Model");
    model.result().report("rpt1").feature("sec1").create("sec1", "Section");
    model.result().report("rpt1").feature("sec1").create("sec2", "Section");
    model.result().report("rpt1").feature("sec1").feature("sec1").create("param1", "Parameter");
    model.result().report("rpt1").feature("sec1").feature("sec2").create("sec1", "Section");
    model.result().report("rpt1").feature("sec1").feature("sec2").feature("sec1")
         .create("mphprop1", "MultiphysicsProp");
    model.result().report("rpt1").feature("sec2").create("comp1", "ModelNode");
    model.result().report("rpt1").feature("sec2").create("sec1", "Section");
    model.result().report("rpt1").feature("sec2").create("sec2", "Section");
    model.result().report("rpt1").feature("sec2").create("sec3", "Section");
    model.result().report("rpt1").feature("sec2").create("sec4", "Section");
    model.result().report("rpt1").feature("sec2").create("sec5", "Section");
    model.result().report("rpt1").feature("sec2").create("sec6", "Section");
    model.result().report("rpt1").feature("sec2").create("sec7", "Section");
    model.result().report("rpt1").feature("sec2").create("sec8", "Section");
    model.result().report("rpt1").feature("sec2").create("sec9", "Section");
    model.result().report("rpt1").feature("sec2").create("sec10", "Section");
    model.result().report("rpt1").feature("sec2").create("sec11", "Section");
    model.result().report("rpt1").feature("sec2").feature("sec1").create("sec1", "Section");
    model.result().report("rpt1").feature("sec2").feature("sec1").create("sec2", "Section");
    model.result().report("rpt1").feature("sec2").feature("sec1").create("sec3", "Section");
    model.result().report("rpt1").feature("sec2").feature("sec1").create("sec4", "Section");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec1").create("sec1", "Section");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec1").create("sec2", "Section");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec1").create("sec3", "Section");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec1").create("sec4", "Section");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec1").create("sec5", "Section");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec1").create("sec6", "Section");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec1").create("sec7", "Section");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec1").feature("sec1")
         .create("var1", "Variables");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec1").feature("sec2")
         .create("var1", "Variables");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec1").feature("sec3")
         .create("var1", "Variables");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec1").feature("sec4")
         .create("var1", "Variables");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec1").feature("sec5")
         .create("var1", "Variables");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec1").feature("sec6")
         .create("var1", "Variables");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec1").feature("sec7")
         .create("var1", "Variables");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec2").create("sec1", "Section");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec2").create("sec2", "Section");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec2").create("sec3", "Section");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec2").feature("sec1")
         .create("func1", "Functions");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec2").feature("sec2")
         .create("func1", "Functions");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec2").feature("sec3")
         .create("func1", "Functions");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec3").create("sec1", "Section");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec3").feature("sec1")
         .create("prb1", "Probe");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec4").create("sec1", "Section");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec4").feature("sec1")
         .create("csys1", "CoordinateSystem");
    model.result().report("rpt1").feature("sec2").feature("sec2").create("geom1", "Geometry");
    model.result().report("rpt1").feature("sec2").feature("sec3").create("sec1", "Section");
    model.result().report("rpt1").feature("sec2").feature("sec3").create("sec2", "Section");
    model.result().report("rpt1").feature("sec2").feature("sec3").feature("sec1").create("mat1", "Material");
    model.result().report("rpt1").feature("sec2").feature("sec3").feature("sec2").create("mat1", "Material");
    model.result().report("rpt1").feature("sec2").feature("sec4").create("sec1", "Section");
    model.result().report("rpt1").feature("sec2").feature("sec4").create("sec2", "Section");
    model.result().report("rpt1").feature("sec2").feature("sec4").create("sec3", "Section");
    model.result().report("rpt1").feature("sec2").feature("sec4").create("sec4", "Section");
    model.result().report("rpt1").feature("sec2").feature("sec4").feature("sec1").create("dg1", "DeformedGeometry");
    model.result().report("rpt1").feature("sec2").feature("sec4").feature("sec2").create("dg1", "DeformedGeometry");
    model.result().report("rpt1").feature("sec2").feature("sec4").feature("sec3").create("dg1", "DeformedGeometry");
    model.result().report("rpt1").feature("sec2").feature("sec4").feature("sec4").create("dg1", "DeformedGeometry");
    model.result().report("rpt1").feature("sec2").feature("sec5").create("phys1", "Physics");
    model.result().report("rpt1").feature("sec2").feature("sec6").create("phys1", "Physics");
    model.result().report("rpt1").feature("sec2").feature("sec7").create("phys1", "Physics");
    model.result().report("rpt1").feature("sec2").feature("sec8").create("phys1", "Physics");
    model.result().report("rpt1").feature("sec2").feature("sec9").create("phys1", "Physics");
    model.result().report("rpt1").feature("sec2").feature("sec10").create("sec1", "Section");
    model.result().report("rpt1").feature("sec2").feature("sec10").create("sec2", "Section");
    model.result().report("rpt1").feature("sec2").feature("sec10").feature("sec1").create("mph1", "Multiphysics");
    model.result().report("rpt1").feature("sec2").feature("sec10").feature("sec2").create("mph1", "Multiphysics");
    model.result().report("rpt1").feature("sec2").feature("sec11").create("mesh1", "Mesh");
    model.result().report("rpt1").feature("sec3").create("std1", "Study");
    model.result().report("rpt1").feature("sec3").create("sec1", "Section");
    model.result().report("rpt1").feature("sec3").feature("sec1").create("sec1", "Section");
    model.result().report("rpt1").feature("sec3").feature("sec1").feature("sec1").create("sol1", "Solver");
    model.result().report("rpt1").feature("sec4").create("sec1", "Section");
    model.result().report("rpt1").feature("sec4").create("sec2", "Section");
    model.result().report("rpt1").feature("sec4").create("sec3", "Section");
    model.result().report("rpt1").feature("sec4").create("sec4", "Section");
    model.result().report("rpt1").feature("sec4").feature("sec1").create("sec1", "Section");
    model.result().report("rpt1").feature("sec4").feature("sec1").create("sec2", "Section");
    model.result().report("rpt1").feature("sec4").feature("sec1").create("sec3", "Section");
    model.result().report("rpt1").feature("sec4").feature("sec1").feature("sec1").create("dset1", "DataSet");
    model.result().report("rpt1").feature("sec4").feature("sec1").feature("sec2").create("dset1", "DataSet");
    model.result().report("rpt1").feature("sec4").feature("sec1").feature("sec3").create("dset1", "DataSet");
    model.result().report("rpt1").feature("sec4").feature("sec2").create("sec1", "Section");
    model.result().report("rpt1").feature("sec4").feature("sec2").create("sec2", "Section");
    model.result().report("rpt1").feature("sec4").feature("sec2").create("sec3", "Section");
    model.result().report("rpt1").feature("sec4").feature("sec2").create("sec4", "Section");
    model.result().report("rpt1").feature("sec4").feature("sec2").feature("sec1").create("num1", "DerivedValues");
    model.result().report("rpt1").feature("sec4").feature("sec2").feature("sec2").create("num1", "DerivedValues");
    model.result().report("rpt1").feature("sec4").feature("sec2").feature("sec3").create("num1", "DerivedValues");
    model.result().report("rpt1").feature("sec4").feature("sec2").feature("sec4").create("num1", "DerivedValues");
    model.result().report("rpt1").feature("sec4").feature("sec3").create("sec1", "Section");
    model.result().report("rpt1").feature("sec4").feature("sec3").feature("sec1").create("mtbl1", "Table");
    model.result().report("rpt1").feature("sec4").feature("sec4").create("sec1", "Section");
    model.result().report("rpt1").feature("sec4").feature("sec4").create("sec2", "Section");
    model.result().report("rpt1").feature("sec4").feature("sec4").create("sec3", "Section");
    model.result().report("rpt1").feature("sec4").feature("sec4").create("sec4", "Section");
    model.result().report("rpt1").feature("sec4").feature("sec4").create("sec5", "Section");
    model.result().report("rpt1").feature("sec4").feature("sec4").create("sec6", "Section");
    model.result().report("rpt1").feature("sec4").feature("sec4").create("sec7", "Section");
    model.result().report("rpt1").feature("sec4").feature("sec4").create("sec8", "Section");
    model.result().report("rpt1").feature("sec4").feature("sec4").create("sec9", "Section");
    model.result().report("rpt1").feature("sec4").feature("sec4").create("sec10", "Section");
    model.result().report("rpt1").feature("sec4").feature("sec4").create("sec11", "Section");
    model.result().report("rpt1").feature("sec4").feature("sec4").feature("sec1").create("pg1", "PlotGroup");
    model.result().report("rpt1").feature("sec4").feature("sec4").feature("sec2").create("pg1", "PlotGroup");
    model.result().report("rpt1").feature("sec4").feature("sec4").feature("sec3").create("pg1", "PlotGroup");
    model.result().report("rpt1").feature("sec4").feature("sec4").feature("sec4").create("pg1", "PlotGroup");
    model.result().report("rpt1").feature("sec4").feature("sec4").feature("sec5").create("pg1", "PlotGroup");
    model.result().report("rpt1").feature("sec4").feature("sec4").feature("sec6").create("pg1", "PlotGroup");
    model.result().report("rpt1").feature("sec4").feature("sec4").feature("sec7").create("pg1", "PlotGroup");
    model.result().report("rpt1").feature("sec4").feature("sec4").feature("sec8").create("pg1", "PlotGroup");
    model.result().report("rpt1").feature("sec4").feature("sec4").feature("sec9").create("pg1", "PlotGroup");
    model.result().report("rpt1").feature("sec4").feature("sec4").feature("sec10").create("pg1", "PlotGroup");
    model.result().report("rpt1").feature("sec4").feature("sec4").feature("sec11").create("pg1", "PlotGroup");

    model.component("comp1").probe("dom1").genResult(null);

    model.result("pg12").tag("pg1");

    model.study("std1").feature("time").set("tlist", "(range(0,2e-9,5e-6))");

    model.sol("sol1").attach("std1");
    model.sol("sol1").feature("st1").label("Compile Equations: Time Dependent");
    model.sol("sol1").feature("v1").label("Dependent Variables 1.1");
    model.sol("sol1").feature("v1").set("clist", new String[]{"(range(0,2e-9,5e-6))[s]", "5.0E-9[s]"});
    model.sol("sol1").feature("v1").feature("comp1_material_disp").set("scalemethod", "manual");
    model.sol("sol1").feature("v1").feature("comp1_material_disp").set("scaleval", 9.319967811103212E-7);
    model.sol("sol1").feature("t1").label("Time-Dependent Solver 1.1");
    model.sol("sol1").feature("t1").set("tlist", "(range(0,2e-9,5e-6))");
    model.sol("sol1").feature("t1").set("rtol", 0.005);
    model.sol("sol1").feature("t1").set("atolglobalfactor", 0.05);
    model.sol("sol1").feature("t1")
         .set("atolmethod", new String[]{"comp1_c", "global", "comp1_material_disp", "global", "comp1_material_disp_lm", "global", "comp1_nitf1_Uave", "global", "comp1_nitf2_Uave", "global", 
         "comp1_p", "scaled", "comp1_p2", "scaled", "comp1_T", "global", "comp1_T2", "global", "comp1_u", "global", 
         "comp1_u2", "global"});
    model.sol("sol1").feature("t1")
         .set("atolfactor", new String[]{"comp1_c", "0.1", "comp1_material_disp", "0.1", "comp1_material_disp_lm", "0.1", "comp1_nitf1_Uave", "0.1", "comp1_nitf2_Uave", "0.1", 
         "comp1_p", "1", "comp1_p2", "1", "comp1_T", "0.1", "comp1_T2", "0.1", "comp1_u", "0.1", 
         "comp1_u2", "0.1"});
    model.sol("sol1").feature("t1").set("maxorder", 2);
    model.sol("sol1").feature("t1").set("stabcntrl", true);
    model.sol("sol1").feature("t1").set("bwinitstepfrac", 0.01);
    model.sol("sol1").feature("t1").set("estrat", "exclude");
    model.sol("sol1").feature("t1").feature("dDef").label("Direct 6");
    model.sol("sol1").feature("t1").feature("aDef").label("Advanced 1");
    model.sol("sol1").feature("t1").feature("aDef").set("cachepattern", true);
    model.sol("sol1").feature("t1").feature("se1").label("Segregated 1.1");
    model.sol("sol1").feature("t1").feature("se1").set("ntolfact", 0.5);
    model.sol("sol1").feature("t1").feature("se1").set("segstabacc", "segaacc");
    model.sol("sol1").feature("t1").feature("se1").set("segaaccdim", 5);
    model.sol("sol1").feature("t1").feature("se1").set("segaaccmix", 0.9);
    model.sol("sol1").feature("t1").feature("se1").feature("ss1").label("Merged Variables");
    model.sol("sol1").feature("t1").feature("se1").feature("ss1")
         .set("segvar", new String[]{"comp1_material_disp", "comp1_material_disp_lm", "comp1_c"});
    model.sol("sol1").feature("t1").feature("se1").feature("ss1").set("linsolver", "d1");
    model.sol("sol1").feature("t1").feature("se1").feature("ss1").set("subdamp", "0.8");
    model.sol("sol1").feature("t1").feature("se1").feature("ss1").set("subjtech", "once");
    model.sol("sol1").feature("t1").feature("se1").feature("ss2").label("Velocity u, Pressure p");
    model.sol("sol1").feature("t1").feature("se1").feature("ss2").set("segvar", new String[]{"comp1_u", "comp1_p"});
    model.sol("sol1").feature("t1").feature("se1").feature("ss2").set("linsolver", "d2");
    model.sol("sol1").feature("t1").feature("se1").feature("ss2").set("subdamp", "0.8");
    model.sol("sol1").feature("t1").feature("se1").feature("ss2").set("subjtech", "once");
    model.sol("sol1").feature("t1").feature("se1").feature("ss3").label("Temperature");
    model.sol("sol1").feature("t1").feature("se1").feature("ss3").set("segvar", new String[]{"comp1_T"});
    model.sol("sol1").feature("t1").feature("se1").feature("ss3").set("linsolver", "d3");
    model.sol("sol1").feature("t1").feature("se1").feature("ss3").set("subdamp", "0.8");
    model.sol("sol1").feature("t1").feature("se1").feature("ss3").set("subjtech", "once");
    model.sol("sol1").feature("t1").feature("se1").feature("ss4").label("Velocity U2, Pressure P2");
    model.sol("sol1").feature("t1").feature("se1").feature("ss4").set("segvar", new String[]{"comp1_u2", "comp1_p2"});
    model.sol("sol1").feature("t1").feature("se1").feature("ss4").set("linsolver", "d4");
    model.sol("sol1").feature("t1").feature("se1").feature("ss4").set("subdamp", "0.8");
    model.sol("sol1").feature("t1").feature("se1").feature("ss4").set("subjtech", "once");
    model.sol("sol1").feature("t1").feature("se1").feature("ss5").label("Temperature (2)");
    model.sol("sol1").feature("t1").feature("se1").feature("ss5").set("segvar", new String[]{"comp1_T2"});
    model.sol("sol1").feature("t1").feature("se1").feature("ss5").set("linsolver", "d5");
    model.sol("sol1").feature("t1").feature("se1").feature("ss5").set("subdamp", "0.8");
    model.sol("sol1").feature("t1").feature("se1").feature("ss5").set("subjtech", "once");
    model.sol("sol1").feature("t1").feature("se1").feature("ll1").label("Lower Limit 1.1");
    model.sol("sol1").feature("t1").feature("se1").feature("ll1").set("lowerlimit", "comp1.T2 0 comp1.T 0 ");
    model.sol("sol1").feature("t1").feature("se1").feature().remove("spf21");
    model.sol("sol1").feature("t1").feature("d1").label("Direct (Merged)");
    model.sol("sol1").feature("t1").feature("d2").label("Direct, fluid flow variables (spf)");
    model.sol("sol1").feature("t1").feature("d2").set("linsolver", "pardiso");
    model.sol("sol1").feature("t1").feature("d2").set("pivotperturb", 1.0E-13);
    model.sol("sol1").feature("t1").feature("d3").label("Direct, heat transfer variables (ht)");
    model.sol("sol1").feature("t1").feature("d3").set("linsolver", "pardiso");
    model.sol("sol1").feature("t1").feature("d3").set("pivotperturb", 1.0E-13);
    model.sol("sol1").feature("t1").feature("d4").label("Direct, fluid flow variables (spf2)");
    model.sol("sol1").feature("t1").feature("d4").set("linsolver", "pardiso");
    model.sol("sol1").feature("t1").feature("d4").set("pivotperturb", 1.0E-13);
    model.sol("sol1").feature("t1").feature("d5").label("Direct, heat transfer variables (ht2)");
    model.sol("sol1").feature("t1").feature("d5").set("linsolver", "pardiso");
    model.sol("sol1").feature("t1").feature("d5").set("pivotperturb", 1.0E-13);
    model.sol("sol1").feature("t1").feature("i1").label("AMG, concentrations (tds)");
    model.sol("sol1").feature("t1").feature("i1").set("maxlinit", 50);
    model.sol("sol1").feature("t1").feature("i1").feature("ilDef").label("Incomplete LU 1");
    model.sol("sol1").feature("t1").feature("i1").feature("mg1").label("Multigrid 1.1");
    model.sol("sol1").feature("t1").feature("i1").feature("mg1").set("prefun", "saamg");
    model.sol("sol1").feature("t1").feature("i1").feature("mg1").set("maxcoarsedof", 50000);
    model.sol("sol1").feature("t1").feature("i1").feature("mg1").set("saamgcompwise", true);
    model.sol("sol1").feature("t1").feature("i1").feature("mg1").set("usesmooth", false);
    model.sol("sol1").feature("t1").feature("i1").feature("mg1").feature("pr").label("Presmoother 1");
    model.sol("sol1").feature("t1").feature("i1").feature("mg1").feature("pr").feature("soDef").label("SOR 1");
    model.sol("sol1").feature("t1").feature("i1").feature("mg1").feature("pr").feature("sl1").label("SOR Line 1.1");
    model.sol("sol1").feature("t1").feature("i1").feature("mg1").feature("pr").feature("sl1")
         .set("linesweeptype", "ssor");
    model.sol("sol1").feature("t1").feature("i1").feature("mg1").feature("pr").feature("sl1").set("iter", 1);
    model.sol("sol1").feature("t1").feature("i1").feature("mg1").feature("pr").feature("sl1").set("linerelax", 0.7);
    model.sol("sol1").feature("t1").feature("i1").feature("mg1").feature("pr").feature("sl1").set("relax", 0.5);
    model.sol("sol1").feature("t1").feature("i1").feature("mg1").feature("po").label("Postsmoother 1");
    model.sol("sol1").feature("t1").feature("i1").feature("mg1").feature("po").feature("soDef").label("SOR 1");
    model.sol("sol1").feature("t1").feature("i1").feature("mg1").feature("po").feature("sl1").label("SOR Line 1.1");
    model.sol("sol1").feature("t1").feature("i1").feature("mg1").feature("po").feature("sl1")
         .set("linesweeptype", "ssor");
    model.sol("sol1").feature("t1").feature("i1").feature("mg1").feature("po").feature("sl1").set("iter", 1);
    model.sol("sol1").feature("t1").feature("i1").feature("mg1").feature("po").feature("sl1").set("linerelax", 0.7);
    model.sol("sol1").feature("t1").feature("i1").feature("mg1").feature("po").feature("sl1").set("relax", 0.5);
    model.sol("sol1").feature("t1").feature("i1").feature("mg1").feature("cs").label("Coarse Solver 1");
    model.sol("sol1").feature("t1").feature("i1").feature("mg1").feature("cs").feature("dDef").label("Direct 2");
    model.sol("sol1").feature("t1").feature("i1").feature("mg1").feature("cs").feature("d1").label("Direct 1.1");
    model.sol("sol1").feature("t1").feature("i1").feature("mg1").feature("cs").feature("d1")
         .set("linsolver", "pardiso");
    model.sol("sol1").feature("t1").feature("i1").feature("mg1").feature("cs").feature("d1")
         .set("pivotperturb", 1.0E-13);
    model.sol("sol1").feature("t1").feature("i2").label("AMG, fluid flow variables (spf)");
    model.sol("sol1").feature("t1").feature("i2").set("maxlinit", 100);
    model.sol("sol1").feature("t1").feature("i2").set("rhob", 20);
    model.sol("sol1").feature("t1").feature("i2").feature("ilDef").label("Incomplete LU 1");
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").label("Multigrid 1.1");
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").set("prefun", "saamg");
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").set("maxcoarsedof", 80000);
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").set("strconn", 0.02);
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").set("saamgcompwise", true);
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").set("usesmooth", false);
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("pr").label("Presmoother 1");
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("pr").feature("soDef").label("SOR 1");
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("pr").feature("sc1").label("SCGS 1.1");
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("pr").feature("sc1")
         .set("linesweeptype", "ssor");
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("pr").feature("sc1").set("iter", 0);
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("pr").feature("sc1").set("approxscgs", true);
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("pr").feature("sc1")
         .set("scgsdirectmaxsize", 1000);
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("po").label("Postsmoother 1");
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("po").feature("soDef").label("SOR 1");
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("po").feature("sc1").label("SCGS 1.1");
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("po").feature("sc1")
         .set("linesweeptype", "ssor");
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("po").feature("sc1").set("iter", 1);
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("po").feature("sc1").set("approxscgs", true);
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("po").feature("sc1")
         .set("scgsdirectmaxsize", 1000);
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("cs").label("Coarse Solver 1");
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("cs").feature("dDef").label("Direct 2");
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("cs").feature("d1").label("Direct 1.1");
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("cs").feature("d1")
         .set("linsolver", "pardiso");
    model.sol("sol1").feature("t1").feature("i2").feature("mg1").feature("cs").feature("d1")
         .set("pivotperturb", 1.0E-13);
    model.sol("sol1").feature("t1").feature("i3").label("AMG, heat transfer variables (ht)");
    model.sol("sol1").feature("t1").feature("i3").set("rhob", 20);
    model.sol("sol1").feature("t1").feature("i3").feature("ilDef").label("Incomplete LU 1");
    model.sol("sol1").feature("t1").feature("i3").feature("mg1").label("Multigrid 1.1");
    model.sol("sol1").feature("t1").feature("i3").feature("mg1").set("prefun", "saamg");
    model.sol("sol1").feature("t1").feature("i3").feature("mg1").set("maxcoarsedof", 50000);
    model.sol("sol1").feature("t1").feature("i3").feature("mg1").set("saamgcompwise", true);
    model.sol("sol1").feature("t1").feature("i3").feature("mg1").set("usesmooth", false);
    model.sol("sol1").feature("t1").feature("i3").feature("mg1").feature("pr").label("Presmoother 1");
    model.sol("sol1").feature("t1").feature("i3").feature("mg1").feature("pr").feature("soDef").label("SOR 2");
    model.sol("sol1").feature("t1").feature("i3").feature("mg1").feature("pr").feature("so1").label("SOR 1.1");
    model.sol("sol1").feature("t1").feature("i3").feature("mg1").feature("pr").feature("so1").set("relax", 0.9);
    model.sol("sol1").feature("t1").feature("i3").feature("mg1").feature("po").label("Postsmoother 1");
    model.sol("sol1").feature("t1").feature("i3").feature("mg1").feature("po").feature("soDef").label("SOR 2");
    model.sol("sol1").feature("t1").feature("i3").feature("mg1").feature("po").feature("so1").label("SOR 1.1");
    model.sol("sol1").feature("t1").feature("i3").feature("mg1").feature("po").feature("so1").set("relax", 0.9);
    model.sol("sol1").feature("t1").feature("i3").feature("mg1").feature("cs").label("Coarse Solver 1");
    model.sol("sol1").feature("t1").feature("i3").feature("mg1").feature("cs").feature("dDef").label("Direct 2");
    model.sol("sol1").feature("t1").feature("i3").feature("mg1").feature("cs").feature("d1").label("Direct 1.1");
    model.sol("sol1").feature("t1").feature("i3").feature("mg1").feature("cs").feature("d1")
         .set("linsolver", "pardiso");
    model.sol("sol1").feature("t1").feature("i3").feature("mg1").feature("cs").feature("d1")
         .set("pivotperturb", 1.0E-13);
    model.sol("sol1").feature("t1").feature("i4").label("AMG, fluid flow variables (spf2)");
    model.sol("sol1").feature("t1").feature("i4").set("maxlinit", 100);
    model.sol("sol1").feature("t1").feature("i4").set("rhob", 20);
    model.sol("sol1").feature("t1").feature("i4").feature("ilDef").label("Incomplete LU 1");
    model.sol("sol1").feature("t1").feature("i4").feature("mg1").label("Multigrid 1.1");
    model.sol("sol1").feature("t1").feature("i4").feature("mg1").set("prefun", "saamg");
    model.sol("sol1").feature("t1").feature("i4").feature("mg1").set("maxcoarsedof", 80000);
    model.sol("sol1").feature("t1").feature("i4").feature("mg1").set("strconn", 0.02);
    model.sol("sol1").feature("t1").feature("i4").feature("mg1").set("saamgcompwise", true);
    model.sol("sol1").feature("t1").feature("i4").feature("mg1").set("usesmooth", false);
    model.sol("sol1").feature("t1").feature("i4").feature("mg1").feature("pr").label("Presmoother 1");
    model.sol("sol1").feature("t1").feature("i4").feature("mg1").feature("pr").feature("soDef").label("SOR 1");
    model.sol("sol1").feature("t1").feature("i4").feature("mg1").feature("pr").feature("sc1").label("SCGS 1.1");
    model.sol("sol1").feature("t1").feature("i4").feature("mg1").feature("pr").feature("sc1")
         .set("linesweeptype", "ssor");
    model.sol("sol1").feature("t1").feature("i4").feature("mg1").feature("pr").feature("sc1").set("iter", 0);
    model.sol("sol1").feature("t1").feature("i4").feature("mg1").feature("pr").feature("sc1").set("approxscgs", true);
    model.sol("sol1").feature("t1").feature("i4").feature("mg1").feature("pr").feature("sc1")
         .set("scgsdirectmaxsize", 1000);
    model.sol("sol1").feature("t1").feature("i4").feature("mg1").feature("po").label("Postsmoother 1");
    model.sol("sol1").feature("t1").feature("i4").feature("mg1").feature("po").feature("soDef").label("SOR 1");
    model.sol("sol1").feature("t1").feature("i4").feature("mg1").feature("po").feature("sc1").label("SCGS 1.1");
    model.sol("sol1").feature("t1").feature("i4").feature("mg1").feature("po").feature("sc1")
         .set("linesweeptype", "ssor");
    model.sol("sol1").feature("t1").feature("i4").feature("mg1").feature("po").feature("sc1").set("iter", 1);
    model.sol("sol1").feature("t1").feature("i4").feature("mg1").feature("po").feature("sc1").set("approxscgs", true);
    model.sol("sol1").feature("t1").feature("i4").feature("mg1").feature("po").feature("sc1")
         .set("scgsdirectmaxsize", 1000);
    model.sol("sol1").feature("t1").feature("i4").feature("mg1").feature("cs").label("Coarse Solver 1");
    model.sol("sol1").feature("t1").feature("i4").feature("mg1").feature("cs").feature("dDef").label("Direct 2");
    model.sol("sol1").feature("t1").feature("i4").feature("mg1").feature("cs").feature("d1").label("Direct 1.1");
    model.sol("sol1").feature("t1").feature("i4").feature("mg1").feature("cs").feature("d1")
         .set("linsolver", "pardiso");
    model.sol("sol1").feature("t1").feature("i4").feature("mg1").feature("cs").feature("d1")
         .set("pivotperturb", 1.0E-13);
    model.sol("sol1").feature("t1").feature("i5").label("AMG, heat transfer variables (ht2)");
    model.sol("sol1").feature("t1").feature("i5").set("rhob", 20);
    model.sol("sol1").feature("t1").feature("i5").feature("ilDef").label("Incomplete LU 1");
    model.sol("sol1").feature("t1").feature("i5").feature("mg1").label("Multigrid 1.1");
    model.sol("sol1").feature("t1").feature("i5").feature("mg1").set("prefun", "saamg");
    model.sol("sol1").feature("t1").feature("i5").feature("mg1").set("maxcoarsedof", 50000);
    model.sol("sol1").feature("t1").feature("i5").feature("mg1").set("saamgcompwise", true);
    model.sol("sol1").feature("t1").feature("i5").feature("mg1").set("usesmooth", false);
    model.sol("sol1").feature("t1").feature("i5").feature("mg1").feature("pr").label("Presmoother 1");
    model.sol("sol1").feature("t1").feature("i5").feature("mg1").feature("pr").feature("soDef").label("SOR 2");

    return model;
  }

  public static Model run5(Model model) {
    model.sol("sol1").feature("t1").feature("i5").feature("mg1").feature("pr").feature("so1").label("SOR 1.1");
    model.sol("sol1").feature("t1").feature("i5").feature("mg1").feature("pr").feature("so1").set("relax", 0.9);
    model.sol("sol1").feature("t1").feature("i5").feature("mg1").feature("po").label("Postsmoother 1");
    model.sol("sol1").feature("t1").feature("i5").feature("mg1").feature("po").feature("soDef").label("SOR 2");
    model.sol("sol1").feature("t1").feature("i5").feature("mg1").feature("po").feature("so1").label("SOR 1.1");
    model.sol("sol1").feature("t1").feature("i5").feature("mg1").feature("po").feature("so1").set("relax", 0.9);
    model.sol("sol1").feature("t1").feature("i5").feature("mg1").feature("cs").label("Coarse Solver 1");
    model.sol("sol1").feature("t1").feature("i5").feature("mg1").feature("cs").feature("dDef").label("Direct 2");
    model.sol("sol1").feature("t1").feature("i5").feature("mg1").feature("cs").feature("d1").label("Direct 1.1");
    model.sol("sol1").feature("t1").feature("i5").feature("mg1").feature("cs").feature("d1")
         .set("linsolver", "pardiso");
    model.sol("sol1").feature("t1").feature("i5").feature("mg1").feature("cs").feature("d1")
         .set("pivotperturb", 1.0E-13);
    model.sol("sol1").runAll();

    model.result().dataset("dset2").label("Probe Solution 2");
    model.result().numerical("int1").set("data", "none");
    model.result().numerical("int1").set("expr", new String[]{"comp1.T", "comp1.T2"});
    model.result().numerical("int2").set("data", "none");
    model.result().numerical("int2").set("expr", new String[]{"comp1.T", "comp1.T2"});
    model.result("pg1").label("Probe Plot Group 1");
    model.result("pg1").set("xlabel", "Time (s)");
    model.result("pg1").set("ylabel", "Temperature (K), Domain Probe 1");
    model.result("pg1").set("legendpos", "upperleft");
    model.result("pg1").set("windowtitle", "Probe Plot 2");
    model.result("pg1").set("xlabelactive", false);
    model.result("pg1").set("ylabelactive", false);
    model.result("pg2").label("Temperature (ht)");
    model.result("pg2").feature("surf1").set("colortable", "HeatCameraLight");
    model.result("pg2").feature("surf1").set("resolution", "normal");
    model.result("pg3").label("Temperature (ht2)");
    model.result("pg3").feature("surf1").set("colortable", "HeatCameraLight");
    model.result("pg3").feature("surf1").set("resolution", "normal");
    model.result("pg4").label("Velocity (spf)");
    model.result("pg4").set("frametype", "spatial");
    model.result("pg4").feature("surf1").label("Surface");
    model.result("pg4").feature("surf1").set("smooth", "internal");
    model.result("pg4").feature("surf1").set("resolution", "normal");
    model.result("pg5").label("Pressure (spf)");
    model.result("pg5").set("frametype", "spatial");
    model.result("pg5").feature("con1").label("Contour");
    model.result("pg5").feature("con1").set("number", 40);
    model.result("pg5").feature("con1").set("levelrounding", false);
    model.result("pg5").feature("con1").set("smooth", "internal");
    model.result("pg5").feature("con1").set("resolution", "normal");
    model.result("pg6").label("Velocity (spf2)");
    model.result("pg6").set("frametype", "spatial");
    model.result("pg6").feature("surf1").label("Surface");
    model.result("pg6").feature("surf1").set("smooth", "internal");
    model.result("pg6").feature("surf1").set("resolution", "normal");
    model.result("pg7").label("Pressure (spf2)");
    model.result("pg7").set("frametype", "spatial");
    model.result("pg7").feature("con1").label("Contour");
    model.result("pg7").feature("con1").set("number", 40);
    model.result("pg7").feature("con1").set("levelrounding", false);
    model.result("pg7").feature("con1").set("smooth", "internal");
    model.result("pg7").feature("con1").set("resolution", "normal");
    model.result("pg8").label("Concentration (tds)");
    model.result("pg8").set("titletype", "custom");
    model.result("pg8").feature("surf1").set("resolution", "normal");
    model.result("pg8").feature("str1").set("expr", new String[]{"tds.tflux_cx", "tds.tflux_cy"});
    model.result("pg8").feature("str1").set("descr", "Total flux (spatial and material frames)");
    model.result("pg8").feature("str1").set("posmethod", "uniform");
    model.result("pg8").feature("str1").set("pointtype", "arrow");
    model.result("pg8").feature("str1").set("arrowcount", 64);
    model.result("pg8").feature("str1").set("arrowlength", "logarithmic");
    model.result("pg8").feature("str1").set("arrowscale", 2.7893936820083792E53);
    model.result("pg8").feature("str1").set("color", "gray");
    model.result("pg8").feature("str1").set("recover", "pprint");
    model.result("pg8").feature("str1").set("arrowcountactive", false);
    model.result("pg8").feature("str1").set("arrowscaleactive", false);
    model.result("pg8").feature("str1").set("resolution", "normal");
    model.result("pg9").label("Temperature and Fluid Flow (nitf1)");
    model.result("pg9").set("showlegendsunit", true);
    model.result("pg9").feature("surf1").label("Fluid Temperature");
    model.result("pg9").feature("surf1").set("colortable", "HeatCameraLight");
    model.result("pg9").feature("surf1").set("smooth", "internal");
    model.result("pg9").feature("surf1").set("resolution", "normal");
    model.result("pg9").feature("arws1").label("Fluid Flow");
    model.result("pg9").feature("arws1").set("expr", new String[]{"nitf1.ux", "nitf1.uy"});
    model.result("pg9").feature("arws1").set("descr", "Velocity field (spatial and material frames)");
    model.result("pg9").feature("arws1").set("xnumber", 30);
    model.result("pg9").feature("arws1").set("ynumber", 30);
    model.result("pg9").feature("arws1").set("arrowtype", "cone");
    model.result("pg9").feature("arws1").set("arrowlength", "logarithmic");
    model.result("pg9").feature("arws1").set("scale", Double.POSITIVE_INFINITY);
    model.result("pg9").feature("arws1").set("scaleactive", false);
    model.result("pg10").label("Temperature and Fluid Flow (nitf2)");
    model.result("pg10").set("showlegendsunit", true);
    model.result("pg10").feature("surf1").label("Fluid Temperature");
    model.result("pg10").feature("surf1").set("colortable", "HeatCameraLight");
    model.result("pg10").feature("surf1").set("smooth", "internal");
    model.result("pg10").feature("surf1").set("resolution", "normal");
    model.result("pg10").feature("arws1").label("Fluid Flow");
    model.result("pg10").feature("arws1").set("expr", new String[]{"nitf2.ux", "nitf2.uy"});
    model.result("pg10").feature("arws1").set("descr", "Velocity field (spatial and material frames)");
    model.result("pg10").feature("arws1").set("xnumber", 30);
    model.result("pg10").feature("arws1").set("ynumber", 30);
    model.result("pg10").feature("arws1").set("arrowtype", "cone");
    model.result("pg10").feature("arws1").set("arrowlength", "logarithmic");
    model.result("pg10").feature("arws1").set("scale", 8.2874138464368E16);
    model.result("pg10").feature("arws1").set("scaleactive", false);
    model.result("pg11").label("Deformed Geometry");
    model.result("pg11").feature("mesh1").set("qualmeasure", "custom");
    model.result("pg11").feature("mesh1").set("qualexpr", "comp1.material.relVol");
    model.result("pg11").feature("mesh1").set("colorrangeunitinterval", false);
    model.result("pg11").feature("mesh1").set("colortable", "TrafficFlow");
    model.result("pg11").feature("mesh1").set("colortabletrans", "nonlinear");
    model.result("pg11").feature("mesh1").set("nonlinearcolortablerev", true);
    model.result("pg11").feature("mesh1").set("resolution", "normal");
    model.result().report("rpt1").set("templatesource", "complete");
    model.result().report("rpt1")
         .set("filename", "/home/xdadmin/Documents/Vital-WORK/2025/EUV_Lithography/OLD_STUFF_TO_DELETE/KUMAR-2D/Kumar_2D.docx");
    model.result().report("rpt1").feature("tp1").label("Kumar 2D demo v5");
    model.result().report("rpt1").feature("tp1").set("author", "Dr. Ntho");
    model.result().report("rpt1").feature("tp1").set("company", "Tech Group");
    model.result().report("rpt1").feature("tp1").set("version", "1");
    model.result().report("rpt1").feature("tp1")
         .set("summary", "This report summarises the physics and boundary conditions set in the Raja Kumar paper for quantification of spatial and temporal evolution of laser-induced plume");
    model.result().report("rpt1").feature("sec1").label("Global Definitions");
    model.result().report("rpt1").feature("sec1").feature("root1").set("includeunitsystem", true);
    model.result().report("rpt1").feature("sec1").feature("sec1").label("Parameters");
    model.result().report("rpt1").feature("sec1").feature("sec2").label("Shared Properties");
    model.result().report("rpt1").feature("sec1").feature("sec2").feature("sec1").label("Default Model Inputs");
    model.result().report("rpt1").feature("sec1").feature("sec2").feature("sec1").set("source", "firstchild");
    model.result().report("rpt1").feature("sec2").label("Component 1");
    model.result().report("rpt1").feature("sec2").feature("comp1").set("includeauthor", true);
    model.result().report("rpt1").feature("sec2").feature("comp1").set("includedatecreated", true);
    model.result().report("rpt1").feature("sec2").feature("comp1").set("includeversion", true);
    model.result().report("rpt1").feature("sec2").feature("comp1").set("includeframes", true);
    model.result().report("rpt1").feature("sec2").feature("comp1").set("includegeomshapeorder", true);
    model.result().report("rpt1").feature("sec2").feature("sec1").label("Definitions");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec1").label("Variables");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec1").feature("sec1")
         .label("Variable 1 Hertz-Knudsen mass flux for evaporation");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec1").feature("sec1")
         .set("source", "firstchild");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec1").feature("sec2")
         .label("Variables 2 Psat");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec1").feature("sec2")
         .set("source", "firstchild");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec1").feature("sec2").feature("var1")
         .set("noderef", "var2");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec1").feature("sec2").feature("var1")
         .set("children", new String[][]{{"Psat", "on"}});
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec1").feature("sec3")
         .label("Variables 3 q_laser");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec1").feature("sec3")
         .set("source", "firstchild");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec1").feature("sec3").feature("var1")
         .set("noderef", "var3");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec1").feature("sec3").feature("var1")
         .set("children", new String[][]{{"q_laser", "on"}});
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec1").feature("sec4")
         .label("Variable 4 Local molar fraction of Sn atoms ");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec1").feature("sec4")
         .set("source", "firstchild");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec1").feature("sec4").feature("var1")
         .set("noderef", "var4");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec1").feature("sec4").feature("var1")
         .set("children", new String[][]{{"phi_m", "on"}});
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec1").feature("sec5")
         .label("Variables 5 Mesh stiffness  S");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec1").feature("sec5")
         .set("source", "firstchild");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec1").feature("sec5").feature("var1")
         .set("noderef", "var5");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec1").feature("sec5").feature("var1")
         .set("children", new String[][]{{"S", "on"}});
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec1").feature("sec6")
         .label("Variables 6 Total mesh displacment dXY");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec1").feature("sec6")
         .set("source", "firstchild");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec1").feature("sec6").feature("var1")
         .set("noderef", "var6");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec1").feature("sec6").feature("var1")
         .set("children", new String[][]{{"dXY", "on"}});
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec1").feature("sec7")
         .label("Variables 7   Evaporation-driven normal velocity");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec1").feature("sec7")
         .set("source", "firstchild");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec1").feature("sec7").feature("var1")
         .set("noderef", "var7");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec1").feature("sec7").feature("var1")
         .set("children", new String[][]{{"v_n", "on"}});
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec2").label("Functions");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec2").feature("sec1").label("Step 1");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec2").feature("sec1")
         .set("source", "firstchild");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec2").feature("sec2")
         .label("Analytical 1");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec2").feature("sec2")
         .set("source", "firstchild");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec2").feature("sec2").feature("func1")
         .set("noderef", "an1");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec2").feature("sec3").label("Analytic 4");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec2").feature("sec3")
         .set("source", "firstchild");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec2").feature("sec3").feature("func1")
         .set("noderef", "an4");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec3").label("Probes");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec3").feature("sec1")
         .label("Domain Probe 1");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec3").feature("sec1")
         .set("source", "firstchild");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec4").label("Coordinate Systems");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec4").feature("sec1")
         .label("Boundary System 1");
    model.result().report("rpt1").feature("sec2").feature("sec1").feature("sec4").feature("sec1")
         .set("source", "firstchild");
    model.result().report("rpt1").feature("sec2").feature("sec2").label("Geometry 1");
    model.result().report("rpt1").feature("sec2").feature("sec2").set("source", "firstchild");
    model.result().report("rpt1").feature("sec2").feature("sec3").label("Materials");
    model.result().report("rpt1").feature("sec2").feature("sec3").feature("sec1").label("Hydrogen");
    model.result().report("rpt1").feature("sec2").feature("sec3").feature("sec1").set("source", "firstchild");
    model.result().report("rpt1").feature("sec2").feature("sec3").feature("sec1").feature("mat1")
         .set("children", new String[][]{{"def", "on", "on"}, {"RadiationHeatTransfer", "on", "on"}});
    model.result().report("rpt1").feature("sec2").feature("sec3").feature("sec2")
         .label("Tin [liquid,tested at 260 \u00b0C (533 K)]");
    model.result().report("rpt1").feature("sec2").feature("sec3").feature("sec2").set("source", "firstchild");
    model.result().report("rpt1").feature("sec2").feature("sec3").feature("sec2").feature("mat1")
         .set("noderef", "mat2");
    model.result().report("rpt1").feature("sec2").feature("sec3").feature("sec2").feature("mat1")
         .set("children", new String[][]{{"def", "on", "on"}, {"ThermalExpansion", "on", "on"}});
    model.result().report("rpt1").feature("sec2").feature("sec4").label("Deformed Geometry");
    model.result().report("rpt1").feature("sec2").feature("sec4").feature("sec1").label("Deforming Domain 1");
    model.result().report("rpt1").feature("sec2").feature("sec4").feature("sec1").set("source", "firstchild");
    model.result().report("rpt1").feature("sec2").feature("sec4").feature("sec2").label("Prescribed Mesh Velocity 2");
    model.result().report("rpt1").feature("sec2").feature("sec4").feature("sec2").set("source", "firstchild");
    model.result().report("rpt1").feature("sec2").feature("sec4").feature("sec2").feature("dg1")
         .set("noderef", "disp2");
    model.result().report("rpt1").feature("sec2").feature("sec4").feature("sec3").label("Deforming Domain 2");
    model.result().report("rpt1").feature("sec2").feature("sec4").feature("sec3").set("source", "firstchild");
    model.result().report("rpt1").feature("sec2").feature("sec4").feature("sec3").feature("dg1")
         .set("noderef", "free2");
    model.result().report("rpt1").feature("sec2").feature("sec4").feature("sec4").label("Fixed Boundary 1");
    model.result().report("rpt1").feature("sec2").feature("sec4").feature("sec4").set("source", "firstchild");
    model.result().report("rpt1").feature("sec2").feature("sec4").feature("sec4").feature("dg1")
         .set("noderef", "fix1");
    model.result().report("rpt1").feature("sec2").feature("sec5").label("Heat Transfer in Fluids");
    model.result().report("rpt1").feature("sec2").feature("sec5").set("source", "firstchild");
    model.result().report("rpt1").feature("sec2").feature("sec6").label("Heat Transfer in Fluids 2");
    model.result().report("rpt1").feature("sec2").feature("sec6").set("source", "firstchild");
    model.result().report("rpt1").feature("sec2").feature("sec6").feature("phys1").set("noderef", "ht2");
    model.result().report("rpt1").feature("sec2").feature("sec7").label("Laminar Flow");
    model.result().report("rpt1").feature("sec2").feature("sec7").set("source", "firstchild");
    model.result().report("rpt1").feature("sec2").feature("sec7").feature("phys1").set("noderef", "spf");
    model.result().report("rpt1").feature("sec2").feature("sec7").feature("phys1")
         .set("children", new String[][]{{"fp1", "on", "on", "on"}, 
         {"init1", "on", "on", "on"}, 
         {"wallbc1", "on", "on", "on"}, 
         {"grav1", "on", "on", "on"}, 
         {"dcont1", "on", "on", "on"}, 
         {"bs1", "on", "on", "on"}});
    model.result().report("rpt1").feature("sec2").feature("sec8").label("Laminar Flow 2");
    model.result().report("rpt1").feature("sec2").feature("sec8").set("source", "firstchild");
    model.result().report("rpt1").feature("sec2").feature("sec8").feature("phys1").set("noderef", "spf2");
    model.result().report("rpt1").feature("sec2").feature("sec8").feature("phys1")
         .set("children", new String[][]{{"fp1", "on", "on", "on"}, 
         {"init1", "on", "on", "on"}, 
         {"wallbc1", "on", "on", "on"}, 
         {"grav1", "on", "on", "on"}, 
         {"dcont1", "on", "on", "on"}, 
         {"bs1", "on", "on", "on"}});
    model.result().report("rpt1").feature("sec2").feature("sec9").label("Transport of Diluted Species");
    model.result().report("rpt1").feature("sec2").feature("sec9").set("source", "firstchild");
    model.result().report("rpt1").feature("sec2").feature("sec9").feature("phys1").set("noderef", "tds");
    model.result().report("rpt1").feature("sec2").feature("sec9").feature("phys1")
         .set("children", new String[][]{{"sp1", "on", "on", "on"}, 
         {"cdm1", "on", "on", "on"}, 
         {"nflx1", "on", "on", "on"}, 
         {"init1", "on", "on", "on"}, 
         {"dcont1", "on", "on", "on"}, 
         {"fl1", "on", "on", "on"}, 
         {"cdm2", "on", "on", "on"}});
    model.result().report("rpt1").feature("sec2").feature("sec10").label("Multiphysics");
    model.result().report("rpt1").feature("sec2").feature("sec10").feature("sec1").label("Nonisothermal Flow 1");
    model.result().report("rpt1").feature("sec2").feature("sec10").feature("sec1").set("source", "firstchild");
    model.result().report("rpt1").feature("sec2").feature("sec10").feature("sec2").label("Nonisothermal Flow 2");
    model.result().report("rpt1").feature("sec2").feature("sec10").feature("sec2").set("source", "firstchild");
    model.result().report("rpt1").feature("sec2").feature("sec10").feature("sec2").feature("mph1")
         .set("noderef", "nitf2");
    model.result().report("rpt1").feature("sec2").feature("sec11").label("Mesh 1");
    model.result().report("rpt1").feature("sec2").feature("sec11").set("source", "firstchild");
    model.result().report("rpt1").feature("sec2").feature("sec11").feature("mesh1").set("includestats", true);
    model.result().report("rpt1").feature("sec3").label("Study 1");
    model.result().report("rpt1").feature("sec3").feature("sec1").label("Solver Configurations");
    model.result().report("rpt1").feature("sec3").feature("sec1").feature("sec1").label("Solution 1");
    model.result().report("rpt1").feature("sec3").feature("sec1").feature("sec1").set("source", "firstchild");
    model.result().report("rpt1").feature("sec3").feature("sec1").feature("sec1").feature("sol1")
         .set("includelog", true);
    model.result().report("rpt1").feature("sec4").label("Results");
    model.result().report("rpt1").feature("sec4").feature("sec1").label("Datasets");
    model.result().report("rpt1").feature("sec4").feature("sec1").feature("sec1").label("Study 1/Solution 1");
    model.result().report("rpt1").feature("sec4").feature("sec1").feature("sec1").set("source", "firstchild");
    model.result().report("rpt1").feature("sec4").feature("sec1").feature("sec2").label("Probe Solution 2");
    model.result().report("rpt1").feature("sec4").feature("sec1").feature("sec2").set("source", "firstchild");
    model.result().report("rpt1").feature("sec4").feature("sec1").feature("sec2").feature("dset1")
         .set("noderef", "dset2");
    model.result().report("rpt1").feature("sec4").feature("sec1").feature("sec3").label("Domain Probe 1");
    model.result().report("rpt1").feature("sec4").feature("sec1").feature("sec3").set("source", "firstchild");
    model.result().report("rpt1").feature("sec4").feature("sec1").feature("sec3").feature("dset1")
         .set("noderef", "avh1");
    model.result().report("rpt1").feature("sec4").feature("sec2").label("Derived Values");
    model.result().report("rpt1").feature("sec4").feature("sec2").feature("sec1").label("Line Integration 1");
    model.result().report("rpt1").feature("sec4").feature("sec2").feature("sec1").set("source", "firstchild");
    model.result().report("rpt1").feature("sec4").feature("sec2").feature("sec2").label("Surface Integration 2");
    model.result().report("rpt1").feature("sec4").feature("sec2").feature("sec2").set("source", "firstchild");
    model.result().report("rpt1").feature("sec4").feature("sec2").feature("sec2").feature("num1")
         .set("noderef", "int2");
    model.result().report("rpt1").feature("sec4").feature("sec2").feature("sec3").label("Volume Integration 3");
    model.result().report("rpt1").feature("sec4").feature("sec2").feature("sec3").set("source", "firstchild");
    model.result().report("rpt1").feature("sec4").feature("sec2").feature("sec3").feature("num1")
         .set("noderef", "int3");
    model.result().report("rpt1").feature("sec4").feature("sec2").feature("sec4").label("Domain Probe 1");
    model.result().report("rpt1").feature("sec4").feature("sec2").feature("sec4").set("source", "firstchild");
    model.result().report("rpt1").feature("sec4").feature("sec2").feature("sec4").feature("num1")
         .set("noderef", "pev1");
    model.result().report("rpt1").feature("sec4").feature("sec3").label("Tables");
    model.result().report("rpt1").feature("sec4").feature("sec3").feature("sec1").label("Probe Table 1");
    model.result().report("rpt1").feature("sec4").feature("sec3").feature("sec1").set("source", "firstchild");
    model.result().report("rpt1").feature("sec4").feature("sec4").label("Plot Groups");
    model.result().report("rpt1").feature("sec4").feature("sec4").feature("sec1").label("Probe Plot Group 1");
    model.result().report("rpt1").feature("sec4").feature("sec4").feature("sec1").set("source", "firstchild");
    model.result().report("rpt1").feature("sec4").feature("sec4").feature("sec1").feature("pg1")
         .set("noderef", "pg1");
    model.result().report("rpt1").feature("sec4").feature("sec4").feature("sec2").label("Temperature (ht)");
    model.result().report("rpt1").feature("sec4").feature("sec4").feature("sec2").set("source", "firstchild");
    model.result().report("rpt1").feature("sec4").feature("sec4").feature("sec3").label("Temperature (ht2)");
    model.result().report("rpt1").feature("sec4").feature("sec4").feature("sec3").set("source", "firstchild");
    model.result().report("rpt1").feature("sec4").feature("sec4").feature("sec3").feature("pg1")
         .set("noderef", "pg3");
    model.result().report("rpt1").feature("sec4").feature("sec4").feature("sec4").label("Velocity (spf)");
    model.result().report("rpt1").feature("sec4").feature("sec4").feature("sec4").set("source", "firstchild");
    model.result().report("rpt1").feature("sec4").feature("sec4").feature("sec4").feature("pg1")
         .set("noderef", "pg4");
    model.result().report("rpt1").feature("sec4").feature("sec4").feature("sec5").label("Pressure (spf)");
    model.result().report("rpt1").feature("sec4").feature("sec4").feature("sec5").set("source", "firstchild");
    model.result().report("rpt1").feature("sec4").feature("sec4").feature("sec5").feature("pg1")
         .set("noderef", "pg5");
    model.result().report("rpt1").feature("sec4").feature("sec4").feature("sec6").label("Velocity (spf2)");
    model.result().report("rpt1").feature("sec4").feature("sec4").feature("sec6").set("source", "firstchild");
    model.result().report("rpt1").feature("sec4").feature("sec4").feature("sec6").feature("pg1")
         .set("noderef", "pg6");
    model.result().report("rpt1").feature("sec4").feature("sec4").feature("sec7").label("Pressure (spf2)");
    model.result().report("rpt1").feature("sec4").feature("sec4").feature("sec7").set("source", "firstchild");
    model.result().report("rpt1").feature("sec4").feature("sec4").feature("sec7").feature("pg1")
         .set("noderef", "pg7");
    model.result().report("rpt1").feature("sec4").feature("sec4").feature("sec8").label("Concentration (tds)");
    model.result().report("rpt1").feature("sec4").feature("sec4").feature("sec8").set("source", "firstchild");
    model.result().report("rpt1").feature("sec4").feature("sec4").feature("sec8").feature("pg1")
         .set("noderef", "pg8");
    model.result().report("rpt1").feature("sec4").feature("sec4").feature("sec9")
         .label("Temperature and Fluid Flow (nitf1)");
    model.result().report("rpt1").feature("sec4").feature("sec4").feature("sec9").set("source", "firstchild");
    model.result().report("rpt1").feature("sec4").feature("sec4").feature("sec9").feature("pg1")
         .set("noderef", "pg9");
    model.result().report("rpt1").feature("sec4").feature("sec4").feature("sec10")
         .label("Temperature and Fluid Flow (nitf2)");
    model.result().report("rpt1").feature("sec4").feature("sec4").feature("sec10").set("source", "firstchild");
    model.result().report("rpt1").feature("sec4").feature("sec4").feature("sec10").feature("pg1")
         .set("noderef", "pg10");
    model.result().report("rpt1").feature("sec4").feature("sec4").feature("sec11").label("Deformed Geometry");
    model.result().report("rpt1").feature("sec4").feature("sec4").feature("sec11").set("source", "firstchild");
    model.result().report("rpt1").feature("sec4").feature("sec4").feature("sec11").feature("pg1")
         .set("noderef", "pg11");

    return model;
  }

  public static void main(String[] args) {
    Model model = run();
    model = run2(model);
    model = run3(model);
    model = run4(model);
    run5(model);
  }

}
