<template>
    <nav class="navbar">
        <span class="title"> <a href="http://localhost:8080/overview">價格追蹤小幫手</a></span>
        <span class="menu-icon" button @click="vanishSwitch">{{ isVisible ? '☰' : '☰' }}</span>
        <ul v-if="isVisible" id="content" class="options">
            <li class="line"><a href="http://localhost:8080/overview">物價概覽</a></li>
            <li class="line"><a href="http://localhost:8080/trending">物價趨勢</a></li>
            <li class="line"><a href="http://localhost:8080/news">相關新聞</a></li>
            <li v-if="!isLoggedIn" class="line"><a href="http://localhost:8080/login">登入</a></li>
            <li v-else @click="logout">Hi, {{getUserName}}! 登出</li>
        </ul>
    </nav>
</template>

<script>

import { useAuthStore } from '@/stores/auth';

export default {
    name: 'NavBar',
    computed: {
        isLoggedIn(){
            const userStore = useAuthStore();
            return userStore.isLoggedIn;
        },
        getUserName(){
            const userStore = useAuthStore();
            return userStore.getUserName;
        }
    },
    data() {
        return {
            isVisible: true, // 用來控制版面的顯示與隱藏
        };
    },
    methods: {
        logout(){
            const userStore = useAuthStore();
            userStore.logout();
        },
        vanishSwitch(){
            this.isVisible = !this.isVisible;
        }
    }
};
</script>

<style scoped>
a{
  text-decoration: none;
}
.navbar {
    display: flex;
    justify-content: space-between;
    background-color: #f3f3f3;
    padding: 1.5em;
    height: 4.5em;
    width: 100%;
    align-items: center;
    box-shadow: 0 0 5px #000000;
}
.options a{
    color:#000000;
}
.navbar ul {
    list-style: none;
    display: flex;
    justify-content: space-around;
}

.title > a{
    font-size: 1.4em;
    font-weight: bold;
    color: #2c3e50;
}

.navbar li {
    color: #575B5D;
    margin: 0 .5em;
    font-size: 1.2em;
}
.navbar li:hover{
    cursor: pointer;
    font-weight: bold;
}

.menu-icon {
    display: none;
}
@media (max-width: 768px) {
            #content{
                display:block;
            }
            .navbar{
                display: flex;
                flex-direction: column;
                width: 100%;
                margin: 0;
            }
            .line{
                display:flex;
                margin: 0;
                border-top: 1px solid gray;
                width: 100%;
            }
            .title{
                display: block;
                position: absolute;
                top: 20px;
                left: 20px;
            }
            .options{
                flex-direction: column;
                align-items: center;
                width: 120%;
                background-color: #f0f0f0;
                position: relative;
                margin: 0px;
                top: 48px;
                gap: 20px;
                border-bottom: 1px solid gray;
                padding-top: 11px;
                border-left: 1px solid gray;
                border-right: 1px solid gray;
            }
            .options a {
                text-align: center;
                width: 100%;
                color:#000000;
                padding-top: 15px;
                padding-bottom: 15px;
            }
            .menu-icon {
                display: block;
                position: absolute;
                top: 20px;
                right: 20px;
                font-size: 20px;
            }
        }
</style>