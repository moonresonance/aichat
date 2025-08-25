package cn.edu.wyu.chatweb.service;

import cn.edu.wyu.chatweb.entity.User;
import com.baomidou.mybatisplus.extension.service.IService;


public interface UserService extends IService<User> {
    User getUserByUsername(String username);

    void insertUser(User user);

    void updateUser(User user);

    void deleteUser(Integer id);
}
