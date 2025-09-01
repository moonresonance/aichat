package cn.edu.wyu.chatweb.service.serviceimp;

import cn.edu.wyu.chatweb.entity.Chat;
import cn.edu.wyu.chatweb.mapper.ChatMapper;
import cn.edu.wyu.chatweb.service.ChatService;
import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;

import java.util.List;

import org.springframework.stereotype.Service;

@Service
public class ChatServiceImp extends ServiceImpl<ChatMapper, Chat> implements ChatService {

    @Override
    public List<Chat> getUserChatsAndSessionId(Integer userId, Integer sessionId) {
       QueryWrapper<Chat> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("user_id",userId).eq("session_id",sessionId);
        return baseMapper.selectList(queryWrapper);
    }

    @Override
    public void insertChat(Chat chat) {
        baseMapper.insert(chat);

    }

    @Override
    public void deleteChaBySessionId(Integer sessionId) {
        QueryWrapper<Chat> queryWrapper = new QueryWrapper<>();
        baseMapper.delete(queryWrapper.eq("session_id",sessionId));
    }
}
