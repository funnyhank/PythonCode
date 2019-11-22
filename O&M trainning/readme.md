
##第一章 一些基础知识
**DI（digital input）**：数字量（又称开关量）输入，自控工程师常说的几个术语之一。主要用来监控一些开关的状态，常见的如断路器合闸为1，分闸为0。阀门关到位和开到位也会用到DI。
**DO（digital output）**：数字量输出，自控常用术语之一。主要用来给阀门发送信号，让执行器打开或者关闭。
**AI（analog input)**:模拟量输入，自控常用术语。常见的仪表信号基本都是AI信号，如流量计流量，压力，液位，温度，阀门开口度等。AI与DI的区别在于，AI是连续的，比如调节阀开口度可以是0～100%区间的任意数值；DI则是离散的，要么0，要么1，就像开关阀，要么全开，要么全关。
**AO（analog output）**：模拟量输出，自控常用术语。在我们工厂里只用来控制调节阀的开口度。
**ABB 800xA**：800xA是ABB控制系统的名称，你可以在这个系统里做很多事情。比如编程（工控编程，不同于C或者python之类的计算机语言），比如画面组态，还可以生成各种报表。
**HMI**：人机界面，就是日常运营过程中一直关注的操作画面。在我们项目有电脑画面和触摸屏画面，通常指的是电脑画面。
**电源**:在自控里常见的电源有24VDC，220VAC，偶尔会用到380VAC。24VDC一般用作控制电源，220VAC一般用作阀门执行器的电源，在来福士项目中有几处仪表用的是220VAC做电源，包括：电磁流量计，东部水箱的超声波液位计。
##第二章 阀门
这里主要指的是电动阀门，有别于其他手动阀门，电动阀上有一个执行器，通过控制执行器里的电机转动来实现阀门开启或关闭。现场常见的电动阀门有两种，电动开关阀和电动调节阀，以下简称开关阀和调节阀。
###开关阀
开关阀只能完全打开或者完全关闭，很难停在中间位置。其主要控制原理图如下：
![开关阀原理图](/image/RCCQ-xv.jpg)
从这张原理图中就可以用到我们第一章里提到的基础知识。
首先开关阀的状态，全开或者全关是DI，通过DI810这个模块接入800xA系统，这样我们在监控画面HMI上就可以看到该阀门的开闭状态了。
其次想要控制这个阀门该怎么做呢？首先要给阀门里的电机提供电源，这里用的就是220VAC，然后通过DO810来控制接触器的触点吸合，然后让220V电源导通从而让执行器电机转动。如果要反向呢？那就DO810的另外一个通道输出让另外一个接触器吸合，同时尚一个接触器断开，从何让阀门往另外一个方向动作。
开关阀就是这么简单。

###调节阀
调节阀可以任意调节阀门的开口度，意思就是除了阀门全开或者全关，还可以停在其他位置。通常阀门的开口度我们用百分比（%）来显示。调节阀的原理图也很简单，一起来看看吧：
![调节阀原理图](/image/rccq-tcv.jpg)
这里用到了3种ABB的模块，DI810用来接收全关到位的信号，AO810用来给执行器指令，让阀门转到想要的位置，AI810用来检测阀门实际的位置。
在RCCQ项目AI810和AO810都是采用的4～20mA电流信号，如果是其他类型的模拟量信号则需要采用其他模块。

##第三章 仪表
仪表是自控系统的眼睛，只有通过仪表才能准确的知道发生了什么，水管里的温度是多少，过滤去前后的压力是多少等，从而为我们做故障判断提供可靠的依据。RCCQ的主要仪表有以下几种。

###流量计
准确的说我们采用的是电磁流量计，流量计是安装在管道上的，是管道的一部分。我们项目采用的是分体式的电磁流量计，其外观如下图：
![流量计外形](/image/FlowMeter.jpg)从外观上可以看出流量计由两部分组成，其中左上为变送器，右边是传感器。传感器里有电磁线圈，可以将测出的流量转换成电信号。变送器则是将电信号转换成自控系统需要的信号，这里的信号根据实际需求可以是4～20mA信号，可以是频率（脉冲）信号，还可以通过通讯方式传递给自控系统。
流量计采用的是220VAC供电，因此在打开仪表查看接线时要格外注意。
流量的量程和管道直径有关系，详细的参数设定要根据仪表手册里的提示去变送器里查看。一定要做到仪表量程和800xA系统里的设置一致。

###压力变送器
RCCQ主要采用的压力变送器如图：![PIT](/image/pit.jpg)
RCCQ压力主要有两个级别，低压和高压，因此压力传感器也有两种规格，0～2400kPa和0～8000kPa。另外西部的压力都是0～1000kPa.
现场采用的压力变送器都是两线制的，不需要额外供电，直接由AI810模块供电，然后变送器传递4～20mA电流信号给AI810模块。

###温度RTD
温度RTD的原理是温度变化时导体的阻值也相应变，因此测得导体的阻值也就得到了相应的温度。
常见的RTD有两线制、三线制和四线制。中学物理我们就学过，通过测量电压和电流就可以计算出电阻，但是由于线路本身也有电阻，串联在回路里就会影响测量的精度，因此人们才想出了三线制和四线制，其目的就是为了消除电缆电阻，得到更精确的温度。RCCQ项目AI830是按照三线制接的，BTU（能量计量表）则是按照四线制接的。三线制和四线制原理都是一样的，就是电压和电流分开检测。
另外测温电阻的种类很多，常见的有PTC，NTC，Pt100,Pt100 等等。RCCQ项目用的主要是Pt100, 为什么叫做Pt100呢，因为它的电阻值在100欧姆左右，要记住这个值，这也是我们判断传感器是否正常的主要手段。用万用表测量阻值，在100欧姆附近就说明传感器和接线没有问题，反之只要排查电缆和传感器的问题。

除了上面提到的三种仪表外，现场还有大量的就地显示仪表，压力表、双金属温度计、压差计等，这些仪表没有接入到自控系统中，其作用主要是用于排查故障，或者与其他传感器仪表做对比。
另外现场有少量的超声波液位计，导波雷达液位，电导率分析仪等，数量较少以后有机会再慢慢介绍。


好了作为自控简介的第一部分，就介绍到这里吧。以后会详细介绍自控图纸，自控系统，800xA等内容。