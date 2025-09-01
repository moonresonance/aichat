package cn.edu.wyu.chatweb.Controller;
import cn.edu.wyu.chatweb.entity.User;
import cn.edu.wyu.chatweb.service.UserService;
import lombok.extern.slf4j.Slf4j;
import cn.edu.wyu.chatweb.entity.Result;
import org.springframework.web.bind.annotation.*;


@RestController
@RequestMapping("/user")
@Slf4j
public class UserController {
    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    @PostMapping("/login")
    public Result<User> login(@RequestBody User user) {
        User user1 = userService.getUserByUsername(user.getName());
        if (user1 == null) {
            return Result.error("用户不存在");
        }
        if (!user1.getPassword().equals(user.getPassword())) {
            return Result.error("密码错误");
        }
        return Result.success(user1);
    }

    @PostMapping("/register")
    public Result<User> register(@RequestBody User user) {
        User user1 = userService.getUserByUsername(user.getName());
        if (user1 != null) {
            return Result.error("用户已存在");
        }
        user.setDeleted(0);
        userService.insertUser(user);
        return Result.success("注册成功");
    }

    @PostMapping("/update")
    public Result<User> update(@RequestBody User user) {
        userService.updateUser(user);
        return Result.success("更新成功");
    }

    @DeleteMapping("/delete")
    public Result<User> delete(@RequestParam("id") Integer id) {
        userService.deleteUser(id);
        return Result.success("删除成功");
    }


}



