package cn.edu.wyu.chatweb.service;

import cn.edu.wyu.chatweb.entity.Session;
import com.baomidou.mybatisplus.extension.service.IService;

import java.util.List;

public interface SessionService extends IService<Session> {

    List<Session> getSessionsByUserId(int userId);
    void addSession(Session session);
    void delSession(int id);
    Session getSession(int id);
}
