def reconcile_lr(booking_df, billing_df):
    booking_lr = set(booking_df["LR_NO"])
    billing_lr = set(billing_df["LR_NO"])

    common_lr = booking_lr & billing_lr
    booking_only_lr = booking_lr - billing_lr
    billing_only_lr = billing_lr - booking_lr

    duplicate_lr_count = billing_df["LR_NO"].value_counts()
    duplicate_lr_count = duplicate_lr_count[
        duplicate_lr_count > 1
    ]

    if(len(common_lr) == 0):
        join_status = "NOT RECOMMENDED"
    else:
        join_status = "RECOMMENDED"

    return {
        "common_lr": common_lr,
        "booking_only_lr": booking_only_lr,
        "billing_only_lr": billing_only_lr,
        "duplicate_lr_count": duplicate_lr_count,
        "join_status": join_status
    }