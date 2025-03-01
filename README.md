# 脊髓DTI分析与可视化工具使用指南

一、软件运行环境准备
如果您没有任何代码基础，请按照以下步骤准备运行环境：

1. 安装Python
访问 Python官网 下载并安装Python 3.8或更高版本
安装时，请确保勾选"Add Python to PATH"选项
2. 安装必要的依赖包
打开命令提示符(Windows)或终端(Mac/Linux)，然后输入以下命令安装所需的软件包：

**pip install numpy vtk pydicom dipy nibabel matplotlib SimpleITK tkinter**
注意：在某些系统上，tkinter可能已经包含在Python安装中，如果安装失败，可以跳过这个包。

3. 保存代码文件
创建一个名为spinal_dti_viewer.py的文本文件
将我之前提供的完整代码复制粘贴到这个文件中
保存文件

二、运行软件
在Windows上运行：
打开命令提示符(按Win+R，输入cmd后回车)
导航到保存spinal_dti_viewer.py的文件夹

*cd 路径\到\您的文件夹*
运行程序

**python spinal_dti_viewer.py**
在Mac/Linux上运行：
打开终端
导航到保存spinal_dti_viewer.py的文件夹

**cd 路径/到/您的文件夹**
运行程序

**python spinal_dti_viewer.py**

三、软件使用指南
1. 加载数据
软件支持两种主要的数据格式：DICOM和NIfTI。

加载DICOM数据：
点击菜单栏中的"文件" → "加载DICOM目录"
在弹出的对话框中，浏览并选择包含DTI DICOM序列的文件夹
软件会自动加载数据并提取b值和梯度方向
数据信息会显示在左侧"数据"选项卡中

加载NIfTI数据：
点击菜单栏中的"文件" → "加载NIfTI文件"
选择NIfTI格式的DTI数据文件(.nii或.nii.gz)
然后，需要加载对应的b值和梯度方向文件：
点击"数据"选项卡中的"加载b值文件"按钮，选择.bval文件
点击"加载梯度方向文件"按钮，选择.bvec文件

2. 数据预处理
在"预处理"选项卡中，您可以选择多种预处理步骤：
勾选需要的预处理选项：
生成脑/脊髓掩码：自动分割脊髓区域
运动校正：校正患者在扫描过程中的运动
涡流校正：校正梯度场产生的涡流伪影
图像去噪：减少图像噪声
偏置场校正：校正射频场不均匀性
点击"执行预处理"按钮开始处理
进度条会显示处理进度，完成后会自动更新显示

3. DTI分析
在"分析"选项卡中：
点击"执行DTI分析"按钮开始张量分析
处理完成后，可以选择查看不同的DTI参数图：
FA (分数各向异性)：组织方向性的度量
MD (平均扩散率)：水分子扩散的平均速率
AD (轴向扩散率)：沿主方向的扩散
RD (径向扩散率)：垂直于主方向的扩散
RGB (方向编码彩色图)：显示纤维走向
下方的图表区域会显示当前参数的直方图分布

5. 纤维追踪
在"分析"选项卡的纤维追踪部分：
设置参数：
FA阈值：设置纤维追踪的FA下限(通常在0.15-0.3之间)
最大角度：相邻步骤间允许的最大角度(通常在30-60度之间)
步长：每一步的长度(毫米)
点击"开始纤维追踪"按钮
处理完成后，会在3D视图中显示纤维束

5. ROI分析
在"ROI"选项卡中：
输入ROI名称(例如"颈髓C3段")
选择ROI创建方式：
矩形ROI：创建矩形区域
圆形ROI：创建圆形区域
自由绘制ROI：手动绘制ROI形状
在主视图中绘制ROI：
对于矩形和圆形ROI：点击并拖动调整大小和位置，右键点击完成
对于自由绘制ROI：点击添加点，右键点击完成
ROI创建完成后，可以在列表中查看所有ROI
选择一个ROI后，点击"分析ROI"按钮查看详细统计数据

7. 视图控制
在"设置"选项卡中：
选择查看方向：
轴向：显示轴向切片
矢状位：显示矢状位切片
冠状位：显示冠状位切片
调整窗宽窗位：使用滑块调整图像对比度
切片控制：使用滑块或键盘上下键更改切片位置
此外，在菜单栏的"视图"中，可以选择"3D视图"查看三维重建

8. 保存结果
在"文件"菜单中：
点击"保存结果"保存所有分析数据，包括：
DTI参数图(FA、MD、AD、RD)
纤维追踪结果
ROI掩码
分析统计数据
点击"导出报告"生成HTML格式的分析报告：
包含患者信息、DTI参数统计、ROI分析结果
可以在浏览器中查看并打印
在"设置"选项卡中，可以设置保存路径。

四、交互技巧
切片浏览：
使用键盘上下键切换切片
使用鼠标滚轮切换切片
使用左右键切换不同的体积(多b值数据)
3D视图交互：
左键旋转视图
右键缩放视图
中键或Shift+左键平移视图
ROI操作：
创建多个ROI进行比较
使用"选择ROI颜色"按钮更改ROI的显示颜色
ROI可以跨切片创建
图表交互：
点击图表区域可以放大查看
右键点击可以保存图表为图像

五、实例操作流程
以下是一个完整的脊髓DTI分析流程示例：
加载数据：
打开软件
点击"文件" → "加载DICOM目录"
选择包含脊髓DTI序列的DICOM文件夹
预处理：
切换到"预处理"选项卡
勾选"生成脊髓掩码"、"运动校正"和"涡流校正"
点击"执行预处理"按钮
DTI分析：
切换到"分析"选项卡
点击"执行DTI分析"按钮
在分析完成后，查看FA图并注意颈髓区域
ROI分析：
切换到"ROI"选项卡
输入ROI名称，如"C3_ROI"
点击"创建矩形ROI"
在颈髓C3区域绘制矩形，右键完成
点击"分析ROI"查看统计数据
纤维追踪：
返回"分析"选项卡
设置FA阈值为0.2，角度为45度
点击"开始纤维追踪"
查看生成的纤维束
保存结果：
点击"文件" → "保存结果"
选择保存目录
点击"文件" → "导出报告"
查看生成的HTML报告

六、常见问题解决
软件无法启动：
确保已正确安装所有依赖包
检查Python版本是否为3.8或更高
无法加载DICOM数据：
确保选择了正确的DICOM目录
检查DICOM序列是否包含DTI数据
尝试选择包含单个序列的子文件夹
预处理或分析失败：
检查数据完整性
确保已成功加载b值和梯度方向
查看日志文件(spinal_dti.log)获取详细错误信息
纤维追踪结果不理想：
调整FA阈值(尝试0.15-0.25的范围)
调整角度阈值(尝试30-60度的范围)
确保预处理步骤已正确执行
画面显示异常：
调整窗宽窗位滑块
尝试不同的颜色映射
检查显卡驱动是否最新
希望这份指南能帮助您顺利使用脊髓DTI分析与可视化工具。如有其他问题，请查阅软件中的"帮助"菜单或联系技术支持。
