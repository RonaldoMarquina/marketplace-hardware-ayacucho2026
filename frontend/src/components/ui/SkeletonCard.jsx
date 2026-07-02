const SkeletonCard = () => (
  <div className="overflow-hidden rounded-[28px] border border-slate-200 bg-white shadow-sm">
    <div className="aspect-[4/3] animate-pulse bg-slate-200" />
    <div className="space-y-4 p-4">
      <div className="h-4 w-24 animate-pulse rounded-full bg-slate-200" />
      <div className="space-y-2">
        <div className="h-4 w-full animate-pulse rounded-full bg-slate-200" />
        <div className="h-4 w-3/4 animate-pulse rounded-full bg-slate-200" />
      </div>
      <div className="h-6 w-32 animate-pulse rounded-full bg-slate-200" />
      <div className="h-4 w-1/2 animate-pulse rounded-full bg-slate-200" />
      <div className="flex justify-between gap-3">
        <div className="h-4 w-28 animate-pulse rounded-full bg-slate-200" />
        <div className="h-4 w-20 animate-pulse rounded-full bg-slate-200" />
      </div>
    </div>
  </div>
)

export default SkeletonCard
