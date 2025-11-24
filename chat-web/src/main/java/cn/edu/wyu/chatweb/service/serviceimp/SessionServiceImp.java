package cn.edu.wyu.chatweb.service.serviceimp;

import cn.edu.wyu.chatweb.entity.Session;
import cn.edu.wyu.chatweb.mapper.SessionMapper;
import cn.edu.wyu.chatweb.service.SessionService;
import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
public class SessionServiceImp extends ServiceImpl<SessionMapper, Session> implements SessionService {

    @Override
    public List<Session> getSessionsByUserId(int userId) {
        QueryWrapper<Session> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("user_id", userId);
        return baseMapper.selectList(queryWrapper);
    }
    @Override
    public void addSession(Session session) {
        baseMapper.insert(session);
    }
    @Override
    public void delSession(int id) {
        baseMapper.deleteById(id);
    }
    @Override
    public Session getSession(int id) {
        return baseMapper.selectById(id);
    }

    @Override
    public void updateSession(Session session) {
        baseMapper.updateById(session);
    }
}