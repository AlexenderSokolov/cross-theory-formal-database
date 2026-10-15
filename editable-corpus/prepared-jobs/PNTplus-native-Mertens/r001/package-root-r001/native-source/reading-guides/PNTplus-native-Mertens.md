# Mertens prime-sum constants and Euler-product asymptotic with error (one native author chain)

Role: guide_only. This reading guide is editorial navigation, not the author proof, a TeX transcription, or a substitute for the native Lean sources.

原作者固定版本：c39a751132c88b6e8080b74c74023fd95b3d8be0。计题单位：Mertens-main-chain。

本组计完整Mertens链：Euler-Maclaurin和素幂分离建立weighted prime sums，partial summation控制1/log x余项；L-series/积分尾极限识别Euler-Mascheroni与Meissel-Mertens常数，再通过收敛的log(1-1/p)+1/p尾和指数转换得到Euler product及O(1/log²x)误差。最后E₃.bound两行/不等式转换不单独升格；H2由原作者常数识别与误差链承担，非API声明数。

原题面与完整proof locators见task JSON及DECLARATION_LOCATORS.json；原作者Lean声明的精确type和假设是权威题面。完整本地import闭包2个模块和13个原外部pin均保留，外部仓库只引用固定URL/revision，不升级。

build_status=not_run_no_runtime。本轮没有运行Lean、#print axioms或独立数学认证。源文件中作者原有#print commands原样保留，但没有产生运行结果。

Strong/Medium同一ψ误差目标；Wiener一般Tauberian/AP链不拆弱PNT和常规后果；Mertens一个完整常数/素积误差链；Erdos392两solution同一构造，不分开计数。
