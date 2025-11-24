package cn.edu.wyu.chatweb.service;

import cn.edu.wyu.chatweb.entity.Chat;
import com.baomidou.mybatisplus.extension.service.IService;

import java.util.List;

public interface ChatService extends IService<Chat> {
    List<Chat> getUserChatsAndSessionId(Integer userId,Integer sessionId);
    void insertChat(Chat chat);
    void deleteChaBySessionId(Integer sessionId);
    void updataChat(Chat chat);
}
