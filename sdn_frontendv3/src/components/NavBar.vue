<template>
  <div>
    <div class="header collapse d-lg-flex p-0" id="headerMenuCollapse">
      <div class="container">
        <div class="row row align-items-center">
          <div class="col col-lg order-lg-first">
            <ul class="nav nav-tabs border-0 flex-column flex-lg-row">
              <li class="nav-item">
                <router-link
                  active-class="active"
                  class="nav-link"
                  aria-current="true"
                  data-toggle="false"
                  to="/"
                >
                  <i class="fe fe-box"></i>Home</router-link>
              </li>
              <li class="nav-item">
                <router-link
                  active-class="active"
                  class="nav-link"
                  aria-current="true"
                  data-toggle="false"
                  to="/device"
                >
                  <i class="fe fe-box"></i>Devices</router-link>
              </li>
              <li class="nav-item">
                <router-link
                  active-class="active"
                  class="nav-link"
                  aria-current="true"
                  data-toggle="false"
                  to="/init"
                >
                  <i class="fe fe-box"></i>Initialization</router-link>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
    <div class="page">
      <div class="page-main">
        <div class="my-3 my-md-5">
          <div class="container">
            <div class="page-header">
              <h1 class="page-title">
                <!-- SDN handmade management -->
              </h1>
            </div>

          </div>
        </div>
      </div>
    </div>
    <footer class="footer">
      <!-- <div class="container">
        <div class="row align-items-center flex-row-reverse">
          <div class="col-auto ml-lg-auto">
            <div class="row align-items-center"></div>
          </div>
          <div class="col-12 col-lg-auto mt-3 mt-lg-0 text-center">
            Copyright © 2021 Developed by
            <a href="https://github.com/theballkyo">MarinePA</a>. Theme by
            <a href="https://codecalm.net" target="_blank">codecalm.net</a> All
            rights reserved. Version {{ version }}
          </div>
        </div>
      </div>
      <link id="vendor" rel="stylesheet" href="../static/assets/css/dashboard.css"> -->
    </footer>
  </div>
</template>
