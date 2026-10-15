# Prime number theorem with classical square-root-log error (complete native author chain)

Role: guide_only. This reading guide is editorial navigation, not the author proof, a TeX transcription, or a substitute for the native Lean sources.

原作者固定版本：c39a751132c88b6e8080b74c74023fd95b3d8be0。计题单位：PNT-strong-chain。

本组计入完整作者主链：smoothed Perron/Mellin反演与矩形移线给定量项，GenStrengthPNT实际平衡平滑误差、截断高度和零自由区域代价；StrongPNT构造logarithmic-derivative uniform log-squared bounds及1/log-height零自由宽度，代入得到exp(-c√log x)。最后StrongPNT两行是组合，H3依据在这些完整原作者承重链，不是包装或代码量。MediumPNT的1/10弱误差同一研究目标版本不另计。

原题面与完整proof locators见task JSON及DECLARATION_LOCATORS.json；原作者Lean声明的精确type和假设是权威题面。完整本地import闭包15个模块和13个原外部pin均保留，外部仓库只引用固定URL/revision，不升级。

build_status=not_run_no_runtime。本轮没有运行Lean、#print axioms或独立数学认证。源文件中作者原有#print commands原样保留，但没有产生运行结果。

Strong/Medium同一ψ误差目标；Wiener一般Tauberian/AP链不拆弱PNT和常规后果；Mertens一个完整常数/素积误差链；Erdos392两solution同一构造，不分开计数。
