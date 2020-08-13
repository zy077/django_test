var vm = new Vue({
    el: "#app",
    data: {
        host: host,
        token : sessionStorage.token || localStorage.token,
        user_id: sessionStorage.user_id || localStorage.user_id,
        form_resetpwd: {
            current_pwd: '',
            new_pwd: '',
            confirm_pwd: ''
        },
        error_current_pwd: false,
        error_new_pwd: false,
        error_confirm_pwd: false,
    },
    methods: {
        reset_pswd: function () {
            // 检查用户输入是否为空
            if (!this.form_resetpwd.current_pwd) {
                this.error_current_pwd = true;
                return false
            }else {
                this.error_current_pwd = false;
            }
            if (!this.form_resetpwd.new_pwd) {
                this.error_new_pwd = true;
                return false
            }else {
                this.error_new_pwd = false;
            }
            if (!this.form_resetpwd.confirm_pwd) {
                this.error_confirm_pwd = true;
                return false
            }else{
                this.error_confirm_pwd = false;
            }
            // 检查用户输入是否符合规则
            if (this.form_resetpwd.new_pwd.length < 8) {
                alert("新密码长度不能少于8位！");
                return false
            }
            // 检查新密码和确认密码是否一致
            if (this.form_resetpwd.new_pwd != this.form_resetpwd.confirm_pwd) {
                alert("确认密码和新密码不一致！");
                return false
            }
            // 发起修改密码的请求
            axios.put(this.host + "/user/" + this.user_id + "/reset_password/", this.form_resetpwd, {
                headers: {
                    "Authorization": "JWT " + this.token
                },
                responseType: "json"
            })
                .then(response => {
                    alert(response.data["message"]);
                })
                .catch(error => {
                    alert(error.response.data["message"]);
                })
        }
    },
});