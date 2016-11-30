-- 未処理の受信データを取得するSQL
FIND_RECEIVED_PROJECTS=
select
  received_message_sequence
from
  ins_project_receive_message
where
  status = '0' and process_id = :processId

GET_RECEIVED_PROJECT=
select
  project_name,
  project_type,
  project_class,
  project_start_date,
  project_end_date,
  client_id,
  project_manager,
  project_leader,
  user_id,
  note,
  sales,
  cost_of_goods_sold,
  sga,
  allocation_of_corp_expenses
from
  ins_project_receive_message
where
  received_message_sequence = :RECEIVED_MESSAGE_SEQUENCE
  and status = '0'

-- ステータスを更新するSQL
UPDATE_STATUS =
update
  ins_project_receive_message
set
  status = :newStatus
where
  received_message_sequence = :id

-- プロセスIDを更新するSQL
UPDATE_PROCESS_ID =
update
  ins_project_receive_message
set
  process_id = :processId
where
  status = '0' and process_id is null

