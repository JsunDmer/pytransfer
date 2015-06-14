#### 采用vw进行训练

# step1: 
vw -d  gxh_data_vw.csv -l 10 -c --passes 25 --loss_function hinge --l2 0.1 -f gxh_vw_model_bin.model
# step 2:
vw -d  gxh_data_vw.csv -t -i gxh_vw_model_bin.model  --invert_hash gxh_vw_model.model
