box.cfg{
    background = false,
    listen='0.0.0.0:3301',
}

local fio = require('fio')
local log = require('log')
local uuid = require('uuid')
local os = require('os')

local function create_user()
    username = os.getenv("DB_USER_NAME")
    password = os.getenv("DB_USER_PASSWORD")
    if not box.schema.user.exists(username) then
        box.schema.user.create(username, { password = password })
    else
        box.schema.user.passwd(username, password)
    end
end

local function init()
    local kv_space = box.schema.space.create("kv", {if_not_exists=true})

    box.space.kv:format({
        { name = 'key', type = 'string'},
        { name = 'value', type = 'any'},
    })


    box.space.kv:create_index('primary', { parts = { 'key' } , if_not_exists=true})

    box.space.kv:insert{'reg', 'wef'}
end

box.once('user', create_user)
box.once('init', init)
