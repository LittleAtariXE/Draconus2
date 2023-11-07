<br />
<div id="intro" align="center">
  <a href="https://github.com/LittleAtariXE/Draconus2">
    <img src="img/d3.jpg" alt="Logo" width="320" height="200">
  </a>

  <h1 align="center">DRACONUS 2</h1>

  <p align="center">
    <h3> This code does NOT promote or encourage any illegal activities! The content of this document is for educational purposes only, intended to raise awareness and learn the Python language and in particular the socket module </h3>
    <h3> May this be a warning to both you and your family. Don't download software that you don't trust. Only download software from reputable software developers and those you trust.</h3>
  </p>
</div>
   <br />
   <div align="center">
    <a href="https://github.com/LittleAtariXE/Draconus2#intro"><strong>Intro »</strong></a>
    <br />
    <br />
    <a href="https://github.com/LittleAtariXE/Draconus2#about">ABOUT</a>
    .
    <a href="https://github.com/LittleAtariXE/Draconus2#whatis">What is Draconus</a>
    .
    <a href="https://github.com/LittleAtariXE/Draconus2#how_works">How Draco Works</a>
    ·
    <a href="https://github.com/github_username/repo_name/issues">Report Bug</a>
    ·
    <a href="https://github.com/github_username/repo_name/issues">Request Feature</a>
   </div>
  <br/>
  
  <div id="about" align="center">
    <h2> ABOUT </h2>
    <h4> I created this project primarily to gain a better understanding of how network sockets work in Python, and also as a fun exploration of Processes and Threads. After many, many... hours of work and testing with network sockets, I can only say one thing: "You can get a serious brain workout!" 😄 </h4>
    <h4> However, it seems to me that I've managed to create servers and clients that, to some extent, can work together (recover connections, avoid hanging, etc.). Nevertheless, strange "things" can still happen, and network sockets may behave in quite peculiar ways. </h4>
    <h4> In any case, I invite you to test and improve this project, as someone else might be able to tame those "network sockets." Good luck!</h4>
  </div>

  

<div id="whatis" align="center">
    <h2> What is "Draconus"? </h2>
    <h4> Draconus is a background-running program. Through another program called "Command Center," we connect to Draconus. Draconus enables the creation of various types of servers. These servers run as separate processes in the background but remain dependent on Draconus. As long as Draconus is running, all servers created by us will keep running.</h4>  
    <h4> The advantage of this setup is that you can safely disconnect from Draconus (using the Command Center), and it will continue to run alongside the servers as "Daemon Processes" in the system. </h4>  
    <h4> Draconus allows you to create an unlimited number of servers (I mean, I didn't introduce any limitations) until your CPU explodes! 😄 Each server is capable of handling connections from multiple clients simultaneously, managing those connections, receiving and sending messages or commands. Feel free to test the endurance of the servers, i.e., how many clients they can handle simultaneously and communicate with.</h4>  
    <h4> You're welcome to test and see how robust these servers are! </h4>
</div>
  

<br/>

<div id="how_works" align="center">
  <br/>
  <h2> How Draco Works </h2>
  <h4>Due to its nature, Draconus operates exclusively on the Linux operating system. Because of its use of the Python `multiprocessing` module, this program may not function properly on Windows. However, client-type programs created using Draconus for connecting to servers are compatible with all systems that have Python installed.</h4>

  <h4>To run Draconus, you execute it as a background process (e.g., by using the "nohup" command). Draconus and every server it creates run continuously in the background as separate processes, each having its own log file.</h4>

</div>
