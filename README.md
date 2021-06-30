<img src="https://user-images.githubusercontent.com/19194931/124039227-e5699f80-d9d8-11eb-824e-c7e895f16853.png" alt="logo" width="200"/>

# pRESTo!
<b>pRESTo!</b> - <b>REST</b> based test automation framework

There are several test automation frameworks that make easier the test automation work abstracting the repetitive work. 

Generating screenshots, reading and writing data from/to databases and sending the test results and/or evidences to the test management tools are examples of this repetitive and mechanical work, that takes a lot of time and deviates the focus of the tester from the work that really makes difference, that is validating the business logic.

Most of these frameworks are structured as libraries that are imported to the automation script. This approach, although common, generates a dependency on this library and a programming language (usually the same one in which this library is written) in our test automation scripts.

The inovation whe are bringing on pResto! is to structure these automation support services on a REST structure. This way, we can call it from whatever language that can deal with REST requests. Isn't it genius?
To make pRESTo! flexible and usable in most enviroments, these services will be built as plugins that are activated and set to work on configuration files. 

The first categories of plugins that we are planning to put on pRESTo!'s MVP are the following:
<ul>
  <li>At least one screenshot plugin</li>
  <li>At least one test management integration plugin (to Testlink)</li>
  <li>At least one data reading plugin, to enable getting input data from </li>
</ul>

You are welcome to download the project, contribute to it and use it on your test automation projects.

# pRESTo!
