# Wiener-Ikehara Tauberian theorem and prime-number/AP consequences (one native author chain)

Role: guide_only. This reading guide is editorial navigation, not the author proof, a TeX transcription, or a substitute for the native Lean sources.

原作者固定版本：c39a751132c88b6e8080b74c74023fd95b3d8be0。计题单位：Wiener-PNT-AP-consequences。

本组保留一般非负系数Dirichlet级数的Fourier-Tauberian核心，limiting Fourier平滑与边界连续性控制、光滑非负Fourier核构造及short-interval bootstrap去掉Chebyshev假设；再用characters及L-series边界值取得AP主项。完整一般Tauberian机制与固定等差数列结论比经典StrongPNT的ψ特殊函数及定量误差更一般/不同，本条不把WeakPNT、pi/nth-prime/Mobius/Liouville/Dirichlet等后果另计。

原题面与完整proof locators见task JSON及DECLARATION_LOCATORS.json；原作者Lean声明的精确type和假设是权威题面。完整本地import闭包9个模块和13个原外部pin均保留，外部仓库只引用固定URL/revision，不升级。

build_status=not_run_no_runtime。本轮没有运行Lean、#print axioms或独立数学认证。源文件中作者原有#print commands原样保留，但没有产生运行结果。

Strong/Medium同一ψ误差目标；Wiener一般Tauberian/AP链不拆弱PNT和常规后果；Mertens一个完整常数/素积误差链；Erdos392两solution同一构造，不分开计数。
