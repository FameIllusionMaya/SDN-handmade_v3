<template>
  <div>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">
    <NavBar/>
    <router-view></router-view>
  </div>
</template>

<script lang="ts">
import NavBar from '@/components/NavBar.vue';


export default{
  components: {
        NavBar,
  },
};
</script>
<style>
body {
  background: rgb(150, 201, 255)
}
</style>
