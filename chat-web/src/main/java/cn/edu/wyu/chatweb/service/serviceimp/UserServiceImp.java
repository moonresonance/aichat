package cn.edu.wyu.chatweb.service.serviceimp;

import cn.edu.wyu.chatweb.entity.User;
import cn.edu.wyu.chatweb.mapper.UserMapper;
import cn.edu.wyu.chatweb.service.UserService;
import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import org.springframework.stereotype.Service;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;

@Service
public class UserServiceImp extends ServiceImpl<UserMapper, User> implements UserService {

    @Override
    public User getUserByUsername(String username) {
        QueryWrapper<User> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("name", username);
        return baseMapper.selectOne(queryWrapper);
    }

    @Override
    public void insertUser(User user) {
        baseMapper.insert(user);
    }

    @Override
    public void updateUser(User user) {
        baseMapper.updateById(user);
    }

    @Override
    public void deleteUser(Integer id) {
        baseMapper.deleteById(id);
    }

}
