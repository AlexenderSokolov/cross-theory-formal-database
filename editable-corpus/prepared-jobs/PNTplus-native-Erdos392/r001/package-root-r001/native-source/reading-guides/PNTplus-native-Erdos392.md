# Erdos problem 392: balanced factorial factorization and paired-factor bound (one native author chain)

Role: guide_only. This reading guide is editorial navigation, not the author proof, a TeX transcription, or a substitute for the native Lean sources.

原作者固定版本：c39a751132c88b6e8080b74c74023fd95b3d8be0。计题单位：Erdos392-factorization。

本组保留factorization balance/score descent及card_bound构造；按small/medium/large prime ranges估计初始score、用valuation与rough/smooth分解压至o(n)，结合Stirling从log(n!)转换为n-n/log n+o(n/log n)的balanced factor count。Solution_2只是把已构造因子配对成≤n²并调整常数，同组不另计。H3来自score改进与prime-range estimates的完整构造，不是Solution末尾Stirling代值或代码规模。

原题面与完整proof locators见task JSON及DECLARATION_LOCATORS.json；原作者Lean声明的精确type和假设是权威题面。完整本地import闭包11个模块和13个原外部pin均保留，外部仓库只引用固定URL/revision，不升级。

build_status=not_run_no_runtime。本轮没有运行Lean、#print axioms或独立数学认证。源文件中作者原有#print commands原样保留，但没有产生运行结果。

Strong/Medium同一ψ误差目标；Wiener一般Tauberian/AP链不拆弱PNT和常规后果；Mertens一个完整常数/素积误差链；Erdos392两solution同一构造，不分开计数。
